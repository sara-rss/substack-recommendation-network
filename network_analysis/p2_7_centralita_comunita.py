"""PARTE 2 - Controlli sulla centralità
 A. a quali comunità appartengono i nodi più centrali
 B. i ponti collegano comunità diverse? Per ogni nodo conto in quali comunità
    stanno i suoi vicini e calcolo il participation coefficient 
 C. la centralità dipende dalla distanza dai seed?
 D. rete diretta: newsletter più raccomandate (in-degree)"""
import json
from pathlib import Path
from collections import Counter
import numpy as np, pandas as pd, networkx as nx
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parent.parent
DATA, PLOTS = ROOT / "data_collection" / "data", ROOT / "network_analysis" / "plots"

# Nodi da esaminare, indicati con un pezzo del loro url
# ponti = alta betweenness; SOLO_CLOSENESS = alta closeness ma grado intermedio
PONTI = ["junot.", "whyisthisinteresting", "//on.substack.com", "seymourhersh", "adamgrant"]
SOLO_CLOSENESS = ["paulkrugman", "thefp.com", "honest-broker", "noahpinion", "auraist"]

# Rete non diretta, centralità e comunità di ogni nodo
nodi = pd.read_csv(DATA / "nodi.csv").set_index("url")
archi = pd.read_csv(DATA / "archi.csv")
G = nx.Graph(); G.add_nodes_from(nodi.index); G.add_edges_from(zip(archi.sorgente, archi.destinazione))
cen = json.load(open(PLOTS / "centralita.json"))
com, et = nodi.comunita.to_dict(), nodi.comunita_etichetta.to_dict()   # {url: numero comunità}, {url: nome comunità}
grandi = {c for c, n in Counter(com.values()).items() if n >= 100}     # comunità principali: almeno 100 nodi
corto = lambda u: u.replace("https://", "").replace(".substack.com", "")
trova = lambda k: next(u for u in G if k in u)                         # primo nodo il cui url contiene k


# Restituisce: participation coefficient del nodo u,
# numero di comunità principali tra i suoi vicini, conteggio dei vicini per comunità
def partecipazione(u):
    cnt = Counter(com[v] for v in G[u]); k = sum(cnt.values())
    return 1 - sum((x / k) ** 2 for x in cnt.values()), len([c for c in cnt if c in grandi]), cnt


P = {u: partecipazione(u)[0] for u in G}

# A. Per ogni misura di centralità: in quali comunità cadono i 10 nodi più centrali
print("=== A. COMUNITÀ DEI NODI PIÙ CENTRALI ===")
for misura in ["degree", "betweenness", "closeness"]:
    top = sorted(cen[misura], key=cen[misura].get, reverse=True)[:10]
    print(f"\ntop 10 {misura}:")
    for c, n in Counter(et[u] for u in top).most_common():
        print(f"  {n:2}  {c}")

# B. Partecipazione dei nodi selezionati, confrontata con due riferimenti:
# i nodi di grado intermedio (30-120) e i 10 hub
print("\n=== B. I PONTI COLLEGANO COMUNITÀ DIVERSE? ===")
gradi = dict(G.degree())
rif = [P[u] for u in G if 30 <= gradi[u] <= 120]
print(f"Riferimento (nodi con grado 30-120, n={len(rif)}): partecipazione mediana {np.median(rif):.2f}, "
      f"90o percentile {np.percentile(rif, 90):.2f}")
print(f"Hub (10 nodi di grado massimo): partecipazione mediana "
      f"{np.median([P[u] for u in sorted(G, key=gradi.get, reverse=True)[:10]]):.2f}")
print(f"\n{'nodo':24} {'grado':>5} {'partecip.':>9} {'comunità vicine':>16} {'% vicini fuori dalla propria':>30}   comunità propria")
for nome, lista in [("ponti (betweenness)", PONTI), ("alta closeness", SOLO_CLOSENESS)]:
    print(f"-- {nome}")
    for k in lista:
        u = trova(k); p, nc, cnt = partecipazione(u)
        fuori = 1 - cnt[com[u]] / gradi[u]   # quota di vicini che stanno in una comunità diversa dalla sua
        print(f"{corto(u):24} {gradi[u]:>5} {p:>9.2f} {nc:>16} {100*fuori:>29.0f}%   {et[u]}")

# Una betweenness alta va insieme a una partecipazione alta? Su tutti i nodi e solo su quelli con grado >= 30
rho = spearmanr([cen["betweenness"][u] for u in G], [P[u] for u in G])[0]
sel = [u for u in G if gradi[u] >= 30]
rho30 = spearmanr([cen["betweenness"][u] for u in sel], [P[u] for u in sel])[0]
print(f"\nSpearman betweenness vs partecipazione: {rho:.3f} (tutti i nodi), {rho30:.3f} (grado >= 30)")

# C. Distanza di ogni nodo dal seed più vicino: se i nodi centrali sono quasi tutti seed o loro vicini,
# la centralità potrebbe essere un effetto del campionamento
print("\n=== C. EFFETTO DEL CAMPIONAMENTO ===")
seed = list(nodi.index[nodi.seed == 1])
dist = nx.multi_source_dijkstra_path_length(G, seed)
print("Nodi per distanza dal seed più vicino:", dict(sorted(Counter(dist.values()).items())))
for misura in ["degree", "betweenness", "closeness"]:
    top = sorted(cen[misura], key=cen[misura].get, reverse=True)[:10]
    r = spearmanr([dist[u] for u in G], [cen[misura][u] for u in G])[0]
    print(f"  {misura:12} top 10: seed {sum(dist[u] == 0 for u in top)}, a distanza 1 {sum(dist[u] == 1 for u in top)}, "
          f"a distanza 2+ {sum(dist[u] >= 2 for u in top)} | Spearman con la distanza dai seed: {r:.3f}")
print("Grado mediano per distanza dai seed:",
      {d: float(np.median([gradi[u] for u in G if dist[u] == d])) for d in sorted(set(dist.values()))})

# D. Rete diretta: il grado non diretto ordina i nodi come l'in-degree (quante volte sono raccomandati)?
print("\n=== D. RETE DIRETTA ===")
print("Spearman grado (non diretto) vs in-degree:",
      round(spearmanr(nodi.loc[list(G)].in_degree, [gradi[u] for u in G])[0], 3))
print("Top 10 in-degree:", [(corto(u), int(v)) for u, v in nodi.in_degree.nlargest(10).items()])