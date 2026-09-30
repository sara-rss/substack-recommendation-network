"""PARTE 2.5 - Centralita': degree, PageRank, betweenness ESATTA (igraph, ~1 minuto),
correlazioni tra le misure e individuazione dei nodi-ponte."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from comune import carica_grafo, carica_grafo_diretto, PLOT_NA, corto

import json
import networkx as nx
from scipy.stats import spearmanr

G, D = carica_grafo(), carica_grafo_diretto()


def top10(d, nome):
    print(f"\n--- top 10 {nome} ---")
    for u, v in sorted(d.items(), key=lambda x: -x[1])[:10]:
        print(f"  {v:.5f}  {corto(u)}")


deg = nx.degree_centrality(G)
pr = nx.pagerank(G)
print("Betweenness esatta (circa 1 minuto)...")
import igraph as ig
_nodi = list(G); _idx = {u: i for i, u in enumerate(_nodi)}
_g = ig.Graph(n=len(_nodi), edges=[(_idx[a], _idx[b]) for a, b in G.edges()])
_n = len(_nodi); _norm = 2 / ((_n - 1) * (_n - 2))            # stessa normalizzazione di networkx
bt = {u: b * _norm for u, b in zip(_nodi, _g.betweenness(directed=False))}
# PageRank sulla rete DIRETTA: qui la direzione conta (essere raccomandati da chi conta)
pr_dir = nx.pagerank(D)
pr_dir = {u: pr_dir.get(u, 0.0) for u in G}

top10(deg, "degree centrality")
top10(pr, "PageRank (non diretto)")
top10(pr_dir, "PageRank (rete diretta)")
top10(bt, "betweenness")

nodi = list(G)
print("\n--- correlazione di Spearman tra le misure ---")
for a, b, na, nb in [(deg, pr, "degree", "PageRank"), (deg, bt, "degree", "betweenness"),
                     (deg, pr_dir, "degree", "PageRank diretto")]:
    rho = spearmanr([a[u] for u in nodi], [b[u] for u in nodi])[0]
    print(f"  {na} vs {nb}: {rho:.3f}")

# nodi-ponte: tra i primi 50 per betweenness ma NON tra i primi 50 per grado
rk_deg = {u: i + 1 for i, u in enumerate(sorted(nodi, key=lambda u: -deg[u]))}
rk_bt = {u: i + 1 for i, u in enumerate(sorted(nodi, key=lambda u: -bt[u]))}
print("\n--- nodi-ponte (top 50 betweenness, fuori dalla top 50 per grado) ---")
for u in sorted(nodi, key=lambda u: rk_bt[u])[:50]:
    if rk_deg[u] > 50:
        print(f"  {corto(u):40} grado {G.degree(u):4} (rank {rk_deg[u]:5}) | rank betweenness {rk_bt[u]}")

json.dump({"degree": deg, "pagerank": pr, "pagerank_diretto": pr_dir, "betweenness": bt},
          open(PLOT_NA / "centralita.json", "w"))
print("\nSalvato centralita.json")
