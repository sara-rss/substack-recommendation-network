"""ESPLORATIVO (non tocca la pipeline) - Prova diversi valori di k per KMeans e produce
il grafico del gomito (inertia) e il silhouette score, per documentare la scelta di k (16)
invece di sceglierla a occhio. Va lanciato dopo 01_clustering_temi.py (usa lingua_nodi.csv). Non scrive ne' cluster_nodi.csv ne' altri file della pipeline:
e' solo un aiuto per decidere. Se si decide di cambiare k, il numero va cambiato a mano
dentro 01_clustering_temi.py (e poi va rilanciato con --forza, sapendo che invalida tutto
cio' che viene dopo in open_problem)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from comune import PLOT_OP, carica_titoli, carica_lingue, vettorizzatore

K_DA_PROVARE = [5, 8, 10, 12, 15, 16, 18, 20, 25, 30]
K_SCELTO = 16                # il k usato in 01_clustering_temi.py
CAMPIONE_SILHOUETTE = 3000   # il silhouette esatto su 14mila nodi e' lento: uso un campione

testi, lingua = carica_titoli(), carica_lingue()
doc = [t for u, t in testi.items() if lingua.get(u) == "en"]
print(f"Newsletter in inglese con testo sufficiente: {len(doc)}")
X = vettorizzatore().fit_transform(doc)

rng = np.random.default_rng(42)
campione = rng.choice(X.shape[0], min(CAMPIONE_SILHOUETTE, X.shape[0]), replace=False)

inertia, silhouette = [], []
for k in K_DA_PROVARE:
    km = KMeans(n_clusters=k, random_state=42, n_init=10).fit(X)
    inertia.append(km.inertia_)
    sil = silhouette_score(X[campione], km.labels_[campione])
    silhouette.append(sil)
    print(f"k={k:3}  inertia={km.inertia_:12.1f}  silhouette={sil:.4f}")

fig, ax = plt.subplots(1, 2, figsize=(11, 4))
ax[0].plot(K_DA_PROVARE, inertia, "o-", color="steelblue")
ax[0].set_xlabel("k (numero di cluster)"); ax[0].set_ylabel("Inertia")
ax[0].set_title("Metodo del gomito"); ax[0].axvline(K_SCELTO, color="crimson", linestyle="--", alpha=0.5)

ax[1].plot(K_DA_PROVARE, silhouette, "o-", color="seagreen")
ax[1].set_xlabel("k (numero di cluster)"); ax[1].set_ylabel("Silhouette score")
ax[1].set_title("Silhouette score (piu' alto = meglio)")
ax[1].axvline(K_SCELTO, color="crimson", linestyle="--", alpha=0.5)
plt.tight_layout(); plt.savefig(PLOT_OP / "scelta_k.png", dpi=150)
print("\nSalvato scelta_k.png (linea rossa tratteggiata = k usato nella pipeline)")
