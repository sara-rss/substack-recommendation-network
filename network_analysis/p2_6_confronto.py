"""PARTE 2 - Confronto con i modelli ER e BA
Ogni modello è generato N_REAL volte: si riportano media e deviazione standard.
Per BA si mostrano m=5 e m=6: il grado medio di BA è circa 2m, e questi due valori
sono i più vicini a quello della rete reale """
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
# Realizzazioni per modello: 10 di default, si può cambiare lanciando con N_REAL=20 python ...
N_REAL = int(os.environ.get('N_REAL', 10))
G = carica_grafo()
n, m = G.number_of_nodes(), G.number_of_edges()


# Calcola tutte le misure di una rete 
# Cammino medio e diametro sono calcolati sulla componente gigante
# Clustering con mode="zero": i nodi con grado < 2 contano come 0, come in networkx
def misura(H):
    nodi = list(H); idx = {u: i for i, u in enumerate(nodi)}
    g = ig.Graph(n=len(nodi), edges=[(idx[a], idx[b]) for a, b in H.edges()])
    comp = g.connected_components()
    gig = comp.giant()
    h = gig.path_length_hist(directed=False)
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

# ER: stessi nodi e stessi archi della rete reale. BA: stessi nodi, ogni nuovo nodo porta m archi.
modelli = {"ER": lambda s: nx.gnm_random_graph(n, m, seed=s),
           "BA m=5": lambda s: nx.barabasi_albert_graph(n, 5, seed=s),
           "BA m=6": lambda s: nx.barabasi_albert_graph(n, 6, seed=s)}

# Genero N_REAL reti per modello e le misuro, tengo i gradi della prima per il grafico
esempio = {}
for nome, gen in modelli.items():
    print(f"Genero e misuro {nome} x{N_REAL}...")
    ris[nome] = []
    for s in range(N_REAL):
        H = gen(s); ris[nome].append(misura(H))
        if s == 0:
            esempio[nome] = [d for _, d in H.degree()]

# Tabella: una riga per misura, una colonna per rete 
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

# Distribuzione del grado in scala log-log: rete reale, una realizzazione ER e una BA m=5
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