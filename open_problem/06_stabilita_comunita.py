"""PARTE 4.2 - Le comunita' sono stabili o dipendono dal seed/dall'algoritmo?
Rieseguo Louvain e Leiden N_RUN volte ciascuno con seed diversi e misuro:
 (a) quanto le partizioni si somigliano tra loro (NMI, ARI);
 (b) per ogni comunita' principale della partizione di riferimento:
     - COESIONE: probabilita' che due suoi nodi finiscano insieme in un'altra esecuzione
       (1 = la comunita' ricompare sempre identica, valori bassi = si spezza);
     - la comunita' con cui viene FUSA piu' spesso, e con che probabilita'.
Uscita: plots/stabilita_comunita.csv e plots/stabilita_matrice.png"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import csv, random, itertools
import numpy as np, igraph as ig, leidenalg as la
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from collections import defaultdict
from sklearn.metrics import normalized_mutual_info_score as nmi, adjusted_rand_score as ari
from comune import carica_grafo, carica_comunita, PLOT_OP

N_RUN, MIN_NODI, CAMPIONE = 30, 100, 5000
G = carica_grafo(); com = carica_comunita()
nodi = list(G); idx = {u: i for i, u in enumerate(nodi)}
g = ig.Graph(n=len(nodi), edges=[(idx[a], idx[b]) for a, b in G.edges()])
rif = np.array([com[u] for u in nodi])

run = {"Louvain": [], "Leiden": []}
for s in range(N_RUN):
    random.seed(s)
    run["Louvain"].append(g.community_multilevel().membership)
    run["Leiden"].append(la.find_partition(g, la.ModularityVertexPartition, seed=s).membership)

for nome, P in run.items():
    ncom = [len(set(p)) for p in P]; Q = [g.modularity(p) for p in P]
    coppie = list(itertools.combinations(P, 2))
    print(f"{nome:8} x{N_RUN}: comunita' {min(ncom)}-{max(ncom)} | modularita' "
          f"{np.mean(Q):.4f} ± {np.std(Q):.4f} | tra esecuzioni NMI "
          f"{np.mean([nmi(a, b) for a, b in coppie]):.3f}, ARI {np.mean([ari(a, b) for a, b in coppie]):.3f}")
    print(f"{'':8} accordo con la partizione di riferimento: NMI "
          f"{np.mean([nmi(rif, p) for p in P]):.3f}, ARI {np.mean([ari(rif, p) for p in P]):.3f}")
print(f"Louvain vs Leiden: NMI {np.mean([nmi(a, b) for a in run['Louvain'][:10] for b in run['Leiden'][:10]]):.3f}")

tutte = np.array(run["Louvain"] + run["Leiden"])
membri = defaultdict(list)
for i, c in enumerate(rif):
    membri[c].append(i)
grandi = sorted((c for c in membri if len(membri[c]) >= MIN_NODI), key=lambda c: -len(membri[c]))
rng = np.random.default_rng(0)


def insieme(A, B):
    """Probabilita' che un nodo di A e uno di B finiscano nella stessa comunita'."""
    a, b = rng.choice(A, CAMPIONE), rng.choice(B, CAMPIONE)
    ok = a != b
    return float((tutte[:, a[ok]] == tutte[:, b[ok]]).mean())


M = np.array([[insieme(membri[a], membri[b]) for b in grandi] for a in grandi])
print(f"\n{'comunita':>9} {'nodi':>6} {'coesione':>9}   fusa piu' spesso con")
with open(PLOT_OP / "stabilita_comunita.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["comunita", "n_nodi", "coesione", "gemella", "prob_fusione"])
    for i, c in enumerate(grandi):
        riga = M[i].copy(); riga[i] = -1; j = int(riga.argmax())
        print(f"{c:>9} {len(membri[c]):>6} {M[i, i]:>9.2f}   com {grandi[j]} ({riga[j]:.2f})")
        w.writerow([c, len(membri[c]), round(M[i, i], 3), grandi[j], round(riga[j], 3)])

plt.figure(figsize=(7, 6))
plt.imshow(M, cmap="Reds", vmin=0, vmax=1); plt.colorbar(label="prob. di finire insieme")
plt.xticks(range(len(grandi)), grandi); plt.yticks(range(len(grandi)), grandi)
for i in range(len(grandi)):
    for j in range(len(grandi)):
        plt.text(j, i, f"{M[i, j]:.2f}", ha="center", va="center", fontsize=7,
                 color="white" if M[i, j] > 0.5 else "black")
plt.title(f"Stabilita' delle comunita' ({2*N_RUN} esecuzioni Louvain+Leiden)")
plt.xlabel("comunita'"); plt.ylabel("comunita'")
plt.tight_layout(); plt.savefig(PLOT_OP / "stabilita_matrice.png", dpi=150)
print("\nSalvati stabilita_comunita.csv e stabilita_matrice.png")
