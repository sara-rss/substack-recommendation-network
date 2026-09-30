"""PARTE 2.6 - Confronto con modelli sintetici ER e BA (stessi n e ~m).
Ogni modello e' generato N_REAL volte: si riportano media e deviazione standard.
BA: il parametro m deve essere intero, quindi si mostrano m=5 (archi un po' sotto la rete
reale) e m=6 (un po' sopra): la rete reale sta in mezzo."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from comune import carica_grafo, PLOT_NA

import json
import numpy as np, networkx as nx, igraph as ig
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from collections import Counter

import os
N_REAL = int(os.environ.get('N_REAL', 10))   # realizzazioni per modello (~15 min in totale)
G = carica_grafo()
n, m = G.number_of_nodes(), G.number_of_edges()


def misura(H):
    nodi = list(H); idx = {u: i for i, u in enumerate(nodi)}
    g = ig.Graph(n=len(nodi), edges=[(idx[a], idx[b]) for a, b in H.edges()])
    comp = g.connected_components()
    gig = comp.giant()
    h = gig.path_length_hist(directed=False)          # un solo passaggio: cammino medio + diametro
    dist = [(int(a), c) for a, _, c in h.bins()]
    apl = sum(d * c for d, c in dist) / sum(c for _, c in dist)
    return {"archi": g.ecount(), "grado_medio": 2 * g.ecount() / g.vcount(),
            "grado_max": max(g.degree()), "componenti": len(comp),
            "gigante_%": 100 * gig.vcount() / g.vcount(),
            "clustering": g.transitivity_avglocal_undirected(mode="zero"),
            "transitivita": g.transitivity_undirected(),
            "cammino_medio": apl, "diametro": max(d for d, _ in dist),
            "assort_grado": g.assortativity_degree()}


print(f"Rete reale: {n} nodi, {m} archi")
ris = {"Reale": [misura(G)]}
modelli = {"ER": lambda s: nx.gnm_random_graph(n, m, seed=s),
           "BA m=5": lambda s: nx.barabasi_albert_graph(n, 5, seed=s),
           "BA m=6": lambda s: nx.barabasi_albert_graph(n, 6, seed=s)}
esempio = {}
for nome, gen in modelli.items():
    print(f"Genero e misuro {nome} x{N_REAL}...")
    ris[nome] = []
    for s in range(N_REAL):
        H = gen(s); ris[nome].append(misura(H))
        if s == 0:
            esempio[nome] = [d for _, d in H.degree()]

chiavi = list(ris["Reale"][0])
print(f"\n{'':16}" + "".join(f"{k:>22}" for k in ris))
tab = {}
for k in chiavi:
    riga = f"{k:16}"
    for nome, lista in ris.items():
        v = np.array([x[k] for x in lista], float)
        tab.setdefault(nome, {})[k] = [v.mean(), v.std()]
        riga += f"{v.mean():>22.4f}" if len(v) == 1 else f"{f'{v.mean():.4f} ± {v.std():.4f}':>22}"
    print(riga)
json.dump(tab, open(PLOT_NA / "confronto.json", "w"), indent=1)

plt.figure(figsize=(8, 6))
serie = [("Reale", [d for _, d in G.degree()], "crimson"), ("ER", esempio["ER"], "orange"),
         ("BA m=5", esempio["BA m=5"], "seagreen")]
for nome, gr, col in serie:
    c = Counter(gr); x = sorted(k for k in c if k > 0)
    plt.scatter(x, [c[k] / len(gr) for k in x], s=12, label=nome, color=col, alpha=0.6)
plt.xscale("log"); plt.yscale("log")
plt.xlabel("Grado (k)"); plt.ylabel("P(k)")
plt.title("Distribuzione del grado: rete reale vs ER vs BA"); plt.legend()
plt.tight_layout(); plt.savefig(PLOT_NA / "confronto_gradi.png", dpi=150)
print("\nSalvati confronto.json e confronto_gradi.png")
