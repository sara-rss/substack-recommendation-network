"""PARTE 2.7 - Controlli sulla centralita' (da lanciare dopo p2_5 e dopo open_problem/10_esporta_rete):
 A. a quali comunita' appartengono i nodi piu' centrali;
 B. i "ponti" collegano davvero comunita' diverse? Per ogni nodo: numero di comunita' principali
    tra i vicini e participation coefficient P = 1 - sum_c (k_c / k)^2
    (0 = tutti i vicini in una sola comunita'; vicino a 1 = vicini sparsi su molte comunita');
 C. effetto del campionamento: la centralita' dipende dalla distanza dai seed?
 D. rete diretta: newsletter piu' raccomandate (in-degree)."""
import json
from pathlib import Path
from collections import Counter
import numpy as np, pandas as pd, networkx as nx
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parent.parent
DATA, PLOTS = ROOT / "data_collection" / "data", ROOT / "network_analysis" / "plots"
PONTI = ["junot.", "whyisthisinteresting", "//on.substack.com", "seymourhersh", "adamgrant"]
SOLO_CLOSENESS = ["paulkrugman", "thefp.com", "honest-broker", "noahpinion", "auraist"]

nodi = pd.read_csv(DATA / "nodi.csv").set_index("url")
archi = pd.read_csv(DATA / "archi.csv")
G = nx.Graph(); G.add_nodes_from(nodi.index); G.add_edges_from(zip(archi.sorgente, archi.destinazione))
cen = json.load(open(PLOTS / "centralita.json"))
com, et = nodi.comunita.to_dict(), nodi.comunita_etichetta.to_dict()
grandi = {c for c, n in Counter(com.values()).items() if n >= 100}
corto = lambda u: u.replace("https://", "").replace(".substack.com", "")
trova = lambda k: next(u for u in G if k in u)


def partecipazione(u):
    cnt = Counter(com[v] for v in G[u]); k = sum(cnt.values())
    return 1 - sum((x / k) ** 2 for x in cnt.values()), len([c for c in cnt if c in grandi]), cnt


P = {u: partecipazione(u)[0] for u in G}

print("=== A. COMUNITA' DEI NODI PIU' CENTRALI ===")
for misura in ["degree", "betweenness", "closeness"]:
    top = sorted(cen[misura], key=cen[misura].get, reverse=True)[:10]
    print(f"\ntop 10 {misura}:")
    for c, n in Counter(et[u] for u in top).most_common():
        print(f"  {n:2}  {c}")

print("\n=== B. I PONTI COLLEGANO COMUNITA' DIVERSE? ===")
gradi = dict(G.degree())
rif = [P[u] for u in G if 30 <= gradi[u] <= 120]
print(f"Riferimento (nodi con grado 30-120, n={len(rif)}): partecipazione mediana {np.median(rif):.2f}, "
      f"90o percentile {np.percentile(rif, 90):.2f}")
print(f"Hub (10 nodi di grado massimo): partecipazione mediana "
      f"{np.median([P[u] for u in sorted(G, key=gradi.get, reverse=True)[:10]]):.2f}")
print(f"\n{'nodo':24} {'grado':>5} {'partecip.':>9} {'comunita vicine':>16} {'% vicini fuori dalla propria':>30}   comunita' propria")
for nome, lista in [("ponti (betweenness)", PONTI), ("alta closeness", SOLO_CLOSENESS)]:
    print(f"-- {nome}")
    for k in lista:
        u = trova(k); p, nc, cnt = partecipazione(u)
        fuori = 1 - cnt[com[u]] / gradi[u]
        print(f"{corto(u):24} {gradi[u]:>5} {p:>9.2f} {nc:>16} {100*fuori:>29.0f}%   {et[u]}")
rho = spearmanr([cen["betweenness"][u] for u in G], [P[u] for u in G])[0]
sel = [u for u in G if gradi[u] >= 30]
rho30 = spearmanr([cen["betweenness"][u] for u in sel], [P[u] for u in sel])[0]
print(f"\nSpearman betweenness vs partecipazione: {rho:.3f} (tutti i nodi), {rho30:.3f} (grado >= 30)")

print("\n=== C. EFFETTO DEL CAMPIONAMENTO ===")
seed = list(nodi.index[nodi.seed == 1])
dist = nx.multi_source_dijkstra_path_length(G, seed)
print("Nodi per distanza dal seed piu' vicino:", dict(sorted(Counter(dist.values()).items())))
for misura in ["degree", "betweenness", "closeness"]:
    top = sorted(cen[misura], key=cen[misura].get, reverse=True)[:10]
    r = spearmanr([dist[u] for u in G], [cen[misura][u] for u in G])[0]
    print(f"  {misura:12} top 10: seed {sum(dist[u] == 0 for u in top)}, a distanza 1 {sum(dist[u] == 1 for u in top)}, "
          f"a distanza 2+ {sum(dist[u] >= 2 for u in top)} | Spearman con la distanza dai seed: {r:.3f}")
print("Grado mediano per distanza dai seed:",
      {d: float(np.median([gradi[u] for u in G if dist[u] == d])) for d in sorted(set(dist.values()))})

print("\n=== D. RETE DIRETTA ===")
print("Spearman grado (non diretto) vs in-degree:",
      round(spearmanr(nodi.loc[list(G)].in_degree, [gradi[u] for u in G])[0], 3))
print("Top 10 in-degree:", [(corto(u), int(v)) for u, v in nodi.in_degree.nlargest(10).items()])