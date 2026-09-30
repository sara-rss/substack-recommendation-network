"""PARTE 4.3 - Quanto sono legati comunita' (topologia) e temi (testo)?
 - assortativita' tematica: le newsletter raccomandano newsletter dello stesso tema?
 - NMI / omogeneita' / completezza tra comunita' e macro-tema;
 - MODELLO NULLO: rimescolo a caso i temi tra i nodi N_PERM volte. Se il legame osservato
   e' molto piu' alto di quello ottenuto a caso, non e' frutto del caso.
Tutto calcolato sui soli nodi con tema utilizzabile; ripetuto anche escludendo la categoria
residuale lifestyle_culture per mostrare che il risultato non dipende da lei."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import json
import numpy as np, networkx as nx
from sklearn.metrics import normalized_mutual_info_score as nmi, homogeneity_completeness_v_measure as hcv
from comune import carica_grafo, carica_attributi, carica_comunita, PLOT_OP

N_PERM = 500
G = carica_grafo(); tema, macro = carica_attributi(); com = carica_comunita()
rng = np.random.default_rng(42)
ris = {}
for nome, esclusi in [("tutti i temi utili", {"unlabeled"}),
                      ("senza lifestyle_culture", {"unlabeled", "lifestyle_culture"})]:
    nodi = [u for u in G if macro.get(u) and macro[u] not in esclusi]
    T = np.array([macro[u] for u in nodi]); C = np.array([com[u] for u in nodi])
    H = G.subgraph(nodi)
    nx.set_node_attributes(H, {u: macro[u] for u in nodi}, "macro")
    ass = nx.attribute_assortativity_coefficient(H, "macro")
    oss = nmi(T, C); hom, comp, _ = hcv(T, C)
    nullo_nmi, nullo_ass = [], []
    att = {u: i for i, u in enumerate(nodi)}
    archi = np.array([(att[a], att[b]) for a, b in H.edges()])
    for _ in range(N_PERM):
        Tp = rng.permutation(T)
        nullo_nmi.append(nmi(Tp, C))
    for _ in range(50):                       # nullo per l'assortativita' (piu' lento)
        Tp = rng.permutation(T)
        nx.set_node_attributes(H, dict(zip(nodi, Tp)), "p")
        nullo_ass.append(nx.attribute_assortativity_coefficient(H, "p"))
    z = (oss - np.mean(nullo_nmi)) / np.std(nullo_nmi)
    print(f"\n=== {nome}: {len(nodi)} nodi, {H.number_of_edges()} archi, "
          f"{len(set(T))} temi, {len(set(C))} comunita' ===")
    print(f"  Assortativita' tematica: {ass:.3f}   (a caso: {np.mean(nullo_ass):.3f} ± {np.std(nullo_ass):.3f})")
    print(f"  NMI comunita'-tema:      {oss:.4f}  (a caso: {np.mean(nullo_nmi):.4f} ± {np.std(nullo_nmi):.4f}; "
          f"z = {z:.0f}; p < {1/N_PERM:.3f})")
    print(f"  Omogeneita': {hom:.4f} | Completezza: {comp:.4f}")
    ris[nome] = {"n": len(nodi), "assortativita": ass, "nmi": oss, "nmi_nullo": float(np.mean(nullo_nmi)),
                 "z": float(z), "omogeneita": hom, "completezza": comp}
print("\nNB: omogeneita' > completezza e' atteso ogni volta che le comunita' sono piu' numerose "
      "dei temi: da solo non e' una prova. La prova e' il confronto col modello nullo.")
json.dump(ris, open(PLOT_OP / "comunita_vs_temi.json", "w"), indent=1)
