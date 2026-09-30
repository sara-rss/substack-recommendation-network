"""PARTE 4.1 - Community detection con Louvain.
Louvain contiene una componente casuale: due esecuzioni danno partizioni un po' diverse.
Per non far dipendere i risultati da un seed fortunato, lo eseguo N_RUN volte e tengo come
PARTIZIONE DI RIFERIMENTO quella piu' "centrale", cioe' la piu' simile in media a tutte le
altre (NMI medio massimo). Uscita: data_collection/data/comunita.csv"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import csv, random
import numpy as np, igraph as ig
from collections import Counter
from sklearn.metrics import normalized_mutual_info_score as nmi
from comune import DATA, carica_grafo

N_RUN = 30
G = carica_grafo()
nodi = list(G); idx = {u: i for i, u in enumerate(nodi)}
g = ig.Graph(n=len(nodi), edges=[(idx[a], idx[b]) for a, b in G.edges()])

P = []
for s in range(N_RUN):
    random.seed(s)                                   # igraph usa il generatore di Python
    P.append(g.community_multilevel().membership)
S = np.array([[nmi(a, b) for b in P] for a in P])
medio = (S.sum(axis=1) - 1) / (N_RUN - 1)
best = int(medio.argmax())
part = P[best]
Q = [g.modularity(p) for p in P]
print(f"{N_RUN} esecuzioni: comunita' {min(len(set(p)) for p in P)}-{max(len(set(p)) for p in P)}, "
      f"modularita' {np.mean(Q):.4f} ± {np.std(Q):.4f}")
print(f"Partizione di riferimento: seed {best} (NMI medio con le altre {medio[best]:.3f}; "
      f"media generale {medio.mean():.3f})")

dim = Counter(part)
grandi = [c for c, n in dim.items() if n >= 100]
print(f"Comunita': {len(dim)} | modularita': {g.modularity(part):.4f}")
print(f"Comunita' principali (>=100 nodi): {len(grandi)}, "
      f"che coprono il {100*sum(dim[c] for c in grandi)/len(part):.1f}% dei nodi")
print("Dimensioni:", sorted(dim.values(), reverse=True))

with open(DATA / "comunita.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["url", "comunita"])
    w.writerows(zip(nodi, part))
print("Salvato comunita.csv")
