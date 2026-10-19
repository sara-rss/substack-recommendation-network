"""PARTE 2.4 - Coefficiente di clustering, transitività, triangoli."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from comune import carica_grafo

import networkx as nx, numpy as np

G = carica_grafo()

# per ogni nodo, quota di coppie di vicini collegate tra loro.
# Il clustering medio è la media sui nodi; la transitività è il rapporto globale triangoli / triple connesse
locale = nx.clustering(G)
cc = np.mean(list(locale.values()))
tr = nx.transitivity(G)
tri = sum(nx.triangles(G).values()) // 3   # ogni triangolo viene contato una volta per ciascuno dei suoi 3 nodi
dens = nx.density(G)
print(f"Clustering medio (media dei coefficienti locali): {cc:.4f}")
print(f"Transitività globale: {tr:.4f}")
print(f"Triangoli: {tri}")
print(f"Clustering atteso in una rete casuale equivalente (= densità): {dens:.6f}")
print(f"Rapporto reale/casuale: {cc/dens:.0f}x")

# Clustering medio per fascia di grado, se cala negli hub è un indizio di struttura gerarchica
print("\nClustering medio per fascia di grado:")
for lo, hi in [(2, 5), (6, 10), (11, 20), (21, 50), (51, 100), (101, 10**6)]:
    v = [locale[u] for u, d in G.degree() if lo <= d <= hi]
    if v:
        print(f"  grado {lo:>3}-{hi if hi < 10**6 else '+':<4}: {np.mean(v):.3f}  ({len(v)} nodi)")