"""PARTE 2.3 - Cammini: cammino medio e diametro ESATTI (BFS da ogni nodo, con igraph:
circa 20 secondi) + distribuzione delle distanze."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from comune import carica_grafo, PLOT_NA

import json
import numpy as np, igraph as ig
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

G = carica_grafo()
nodi = list(G); idx = {u: i for i, u in enumerate(nodi)}
g = ig.Graph(n=len(nodi), edges=[(idx[a], idx[b]) for a, b in G.edges()])

apl = g.average_path_length(directed=False)
diam = g.diameter(directed=False)
h = g.path_length_hist(directed=False)
dist = {int(a): int(c) for a, _, c in h.bins()}
tot = sum(dist.values())
print(f"Cammino medio (esatto): {apl:.4f}")
print(f"Diametro (esatto):      {diam}")
print("Distribuzione delle distanze tra coppie di nodi:")
cum = 0
for d in sorted(dist):
    cum += dist[d]
    print(f"  distanza {d}: {100*dist[d]/tot:5.1f}%   (cumulata {100*cum/tot:5.1f}%)")

n = g.vcount(); k = 2 * g.ecount() / n
print(f"\nRiferimento rete casuale: ln(N)/ln(<k>) = {np.log(n)/np.log(k):.2f}")
json.dump({"cammino_medio": apl, "diametro": diam, "distanze": dist},
          open(PLOT_NA / "cammini.json", "w"), indent=1)

plt.figure(figsize=(6, 4))
plt.bar(list(dist), [100 * v / tot for v in dist.values()], color="steelblue")
plt.xlabel("Distanza"); plt.ylabel("% di coppie di nodi")
plt.title("Distribuzione delle distanze")
plt.tight_layout(); plt.savefig(PLOT_NA / "distanze.png", dpi=150)
print("Salvati cammini.json e distanze.png")
