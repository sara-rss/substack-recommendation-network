"""PARTE 2 - Centralità: degree, betweenness e closeness,
correlazioni tra le misure e individuazione dei nodi-ponte"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from comune import carica_grafo, PLOT_NA, corto

import json
import igraph as ig
import networkx as nx
from scipy.stats import spearmanr

G = carica_grafo()
nodi = list(G)


# stampa i 10 nodi con il valore più alto
def top10(d, nome):
    print(f"\n--- top 10 {nome} ---")
    for u, v in sorted(d.items(), key=lambda x: -x[1])[:10]:
        print(f"  {v:.5f}  {corto(u)}")


# posizione di ogni nodo nella classifica di una misura (1 = il più alto)
def classifica(d):
    return {u: i + 1 for i, u in enumerate(sorted(nodi, key=lambda u: -d[u]))}


deg = nx.degree_centrality(G)

# betweenness e closeness esatte con igraph (molto più veloce di networkx)
print("Betweenness e closeness esatte (circa 1 minuto)...")
idx = {u: i for i, u in enumerate(nodi)}
g = ig.Graph(n=len(nodi), edges=[(idx[a], idx[b]) for a, b in G.edges()])
n = len(nodi)
norm = 2 / ((n - 1) * (n - 2))                     # stessa normalizzazione di networkx
bt = {u: b * norm for u, b in zip(nodi, g.betweenness(directed=False))}
cl = {u: c for u, c in zip(nodi, g.closeness())}

top10(deg, "degree centrality")
top10(bt, "betweenness")
top10(cl, "closeness")

print("\n--- correlazione di Spearman tra le misure ---")
for a, b, na, nb in [(deg, bt, "degree", "betweenness"), (deg, cl, "degree", "closeness")]:
    rho = spearmanr([a[u] for u in nodi], [b[u] for u in nodi])[0]
    print(f"  {na} vs {nb}: {rho:.3f}")

rk_deg, rk_bt, rk_cl = classifica(deg), classifica(bt), classifica(cl)

# nodi-ponte: tra i primi 50 per betweenness ma fuori dai primi 50 per grado
print("\n--- nodi-ponte (top 50 betweenness, fuori dalla top 50 per grado) ---")
for u in sorted(nodi, key=lambda u: rk_bt[u])[:50]:
    if rk_deg[u] > 50:
        print(f"  {corto(u):40} grado {G.degree(u):4} (rank {rk_deg[u]:5}) | rank betweenness {rk_bt[u]}")

print("\nIn top 10 closeness ma non in top 10 degree:",
      [(corto(u), G.degree(u), rk_deg[u]) for u in sorted(nodi, key=lambda u: rk_cl[u])[:10] if rk_deg[u] > 10])

json.dump({"degree": deg, "betweenness": bt, "closeness": cl}, open(PLOT_NA / "centralita.json", "w"))
print("\nSalvato centralita.json")