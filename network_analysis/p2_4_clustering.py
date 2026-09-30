"""PARTE 2.4 - Coefficiente di clustering, transitivita', triangoli."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from comune import carica_grafo

import networkx as nx, numpy as np

G = carica_grafo()
locale = nx.clustering(G)
cc = np.mean(list(locale.values()))
tr = nx.transitivity(G)
tri = sum(nx.triangles(G).values()) // 3
dens = nx.density(G)
print(f"Clustering medio (media dei coefficienti locali): {cc:.4f}")
print(f"Transitivita' globale: {tr:.4f}")
print(f"Triangoli: {tri}")
print(f"Clustering atteso in una rete casuale equivalente (= densita'): {dens:.6f}")
print(f"Rapporto reale/casuale: {cc/dens:.0f}x")

# clustering in funzione del grado: negli hub cala (struttura gerarchica)
print("\nClustering medio per fascia di grado:")
for lo, hi in [(2, 5), (6, 10), (11, 20), (21, 50), (51, 100), (101, 10**6)]:
    v = [locale[u] for u, d in G.degree() if lo <= d <= hi]
    if v:
        print(f"  grado {lo:>3}-{hi if hi < 10**6 else '+':<4}: {np.mean(v):.3f}  ({len(v)} nodi)")
