"""Ultimo passo: completa il DATASET FINALE in data_collection/data/.
 - nodi.csv: una riga per newsletter con tutti gli attributi
     url, seed, lingua, tema, macro_tema, comunita, comunita_etichetta, comunita_label,
     grado, in_degree, out_degree
   (tema = 'senza_testo' se non c'era testo; macro_tema = 'unlabeled' se il tema non e' ricavabile;
    comunita_etichetta = 'marginale' per le comunita' con meno di 100 nodi;
    comunita_label = nome inglese usato in figura e nelle tabelle, da stile_rete.COMUNITA)
 - grafo_finale.gexf: la rete non diretta con gli stessi attributi e lo stile gia' applicato
   (colore per comunita', dimensione per grado, posizioni ForceAtlas2 da data/posizioni_fa2.csv
   se presente), da aprire con Gephi.
archi.csv (sorgente, destinazione, reciproca) e' gia' scritto da data_collection/03_costruisci_rete.py.
Stile e parametri del layout sono in stile_rete.py (radice della repository), condiviso con 12_figura_rete.py."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import csv
import networkx as nx
import pandas as pd
from comune import DATA, PLOT_OP, carica_grafo, carica_attributi, carica_comunita, carica_lingue
from stile_rete import NOME_EN, COLORE, FILE_POSIZIONI, dimensione_nodo, rgb

G = carica_grafo(); tema, macro = carica_attributi(); com = carica_comunita(); lingua = carica_lingue()
et = {int(r["comunita"]): r["etichetta"] for r in csv.DictReader(open(PLOT_OP / "comunita_etichette.csv"))}

base = pd.read_csv(DATA / "nodi.csv")[["url", "seed", "in_degree", "out_degree"]]
etichetta = base.url.map(lambda u: et.get(com[u], "marginale"))
nodi = pd.DataFrame({
    "url": base.url, "seed": base.seed,
    "lingua": base.url.map(lambda u: lingua.get(u, "senza_testo")),
    "tema": base.url.map(lambda u: tema.get(u, "senza_testo")),
    "macro_tema": base.url.map(lambda u: macro.get(u, "unlabeled")),
    "comunita": base.url.map(com),
    "comunita_etichetta": etichetta,
    "comunita_label": etichetta.map(NOME_EN),
    "grado": base.url.map(dict(G.degree())),
    "in_degree": base.in_degree, "out_degree": base.out_degree,
})
assert nodi.comunita.notna().all() and len(nodi) == G.number_of_nodes()
mancanti = set(nodi.comunita_etichetta) - set(COLORE)
assert not mancanti, f"etichette senza colore/nome in stile_rete.COMUNITA: {mancanti}"
nodi.to_csv(DATA / "nodi.csv", index=False)

for col in ["seed", "lingua", "tema", "macro_tema", "comunita", "comunita_etichetta", "comunita_label",
            "grado", "in_degree", "out_degree"]:
    nx.set_node_attributes(G, dict(zip(nodi.url, nodi[col].map(lambda v: v.item() if hasattr(v, "item") else v))), col)

# --- stile Gephi (namespace viz del GEXF): colore, dimensione, posizione ---
pos_file = DATA / FILE_POSIZIONI
pos = pd.read_csv(pos_file).set_index("url") if pos_file.exists() else None
if pos is not None:
    assert set(pos.index) == set(G.nodes), f"{FILE_POSIZIONI} non copre esattamente i nodi del grafo"
else:
    print(f"ATTENZIONE: {pos_file} non trovato, GEXF senza posizioni (rifare ForceAtlas2 in Gephi)")
grado_max = int(nodi.grado.max())
for u, e, g in zip(nodi.url, nodi.comunita_etichetta, nodi.grado):
    r, gg, b = rgb(COLORE[e])
    viz = {"color": {"r": r, "g": gg, "b": b, "a": 1.0}, "size": round(dimensione_nodo(int(g), grado_max), 3)}
    if pos is not None:
        viz["position"] = {"x": float(pos.at[u, "x"]), "y": float(pos.at[u, "y"]), "z": 0.0}
    G.nodes[u]["viz"] = viz
nx.write_gexf(G, DATA / "grafo_finale.gexf")

print(f"Salvati data/nodi.csv ({len(nodi)} nodi, {nodi.shape[1]} colonne) e data/grafo_finale.gexf "
      f"({G.number_of_edges()} archi non diretti, posizioni {'incluse' if pos is not None else 'assenti'})")
print(nodi.comunita_label.value_counts().to_string())
print(nodi.head(3).to_string(index=False))
