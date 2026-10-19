"""PARTE 4.1 - Community detection con Louvain.
Per non far dipendere i risultati da un seed fortunato, lo eseguo N_RUN volte e tengo come
partizione di riferimento quella più "centrale" (NMI medio massimo con le altre)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import csv, random
import numpy as np, igraph as ig
from collections import Counter
from sklearn.metrics import normalized_mutual_info_score as nmi
from comune import ELAB, carica_grafo

N_RUN = 30

# Converto la rete da networkx a igraph (nodi numerati da 0)
G = carica_grafo()
nodi = list(G); idx = {u: i for i, u in enumerate(nodi)}
g = ig.Graph(n=len(nodi), edges=[(idx[a], idx[b]) for a, b in G.edges()])

# Louvain N_RUN volte con seed diversi
P = []
for s in range(N_RUN):
    random.seed(s)
    P.append(g.community_multilevel().membership)   # membership = numero di comunità di ogni nodo

# NMI tra ogni coppia di partizioni (1 = identiche, 0 = indipendenti).
# Per ogni partizione faccio la media con le altre, togliendo il confronto con sé stessa 
# e scelgo come riferimento quella più simile in media a tutte le altre
S = np.array([[nmi(a, b) for b in P] for a in P])
medio = (S.sum(axis=1) - 1) / (N_RUN - 1)
best = int(medio.argmax())
part = P[best]

# Riepilogo sulle N_RUN esecuzioni: numero di comunità (min-max) e modularità 
Q = [g.modularity(p) for p in P]
print(f"{N_RUN} esecuzioni: comunità {min(len(set(p)) for p in P)}-{max(len(set(p)) for p in P)}, "
      f"modularità {np.mean(Q):.4f} ± {np.std(Q):.4f}")
print(f"Partizione di riferimento: seed {best} (NMI medio con le altre {medio[best]:.3f}; "
      f"media generale {medio.mean():.3f})")

# Dimensioni delle comunità della partizione scelta; "principali" = almeno 100 nodi
dim = Counter(part)
grandi = [c for c, n in dim.items() if n >= 100]
print(f"Comunità: {len(dim)} | modularità: {g.modularity(part):.4f}")
print(f"Comunità principali (>=100 nodi): {len(grandi)}, "
      f"che coprono il {100*sum(dim[c] for c in grandi)/len(part):.1f}% dei nodi")
print("Dimensioni:", sorted(dim.values(), reverse=True))

with open(ELAB / "comunita.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["url", "comunita"])
    w.writerows(zip(nodi, part))
print("Salvato comunita.csv")