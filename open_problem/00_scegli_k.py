"""Prova diversi valori di k per KMeans e produce il grafico del gomito (inertia)
e il silhouette score, per documentare la scelta di k (16)."""
import sys
from pathlib import Path

# Aggiunge la cartella padre al path per poter importare il modulo comune
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import matplotlib; matplotlib.use("Agg") 
import matplotlib.pyplot as plt
from comune import PLOT_OP, carica_titoli, carica_lingue, vettorizzatore

K_DA_PROVARE = [5, 8, 10, 12, 15, 16, 18, 20, 25, 30]  # provo 10 k da 5 a 30
K_SCELTO = 16                # Il k usato in 01_clustering_temi
CAMPIONE_SILHOUETTE = 3000   # Scelgo un campione di newsletter per ottimizzare tempo e memoria

# Uso solo newsletter in inglese, in modo tale che i k siano rappresentativi per 01_clustering_temi
testi, lingua = carica_titoli(), carica_lingue()
doc = [t for u, t in testi.items() if lingua.get(u) == "en"]
print(f"Newsletter in inglese con testo sufficiente: {len(doc)}")

# Vettorizzatore che si trova nel modulo comune: TF-IDF
X = vettorizzatore().fit_transform(doc)

# Scelgo casualmente 3000 newsletter su cui calcolare il silhouette
rng = np.random.default_rng(42)
campione = rng.choice(X.shape[0], min(CAMPIONE_SILHOUETTE, X.shape[0]), replace=False)

inertia, silhouette = [], []
for k in K_DA_PROVARE:
    # KMeans viene addestrato su tutte le newsletter
    km = KMeans(n_clusters=k, random_state=42, n_init=10).fit(X) #KMeans prova 10 volte partendo da punti diversi e tiene il risultato migliore

    # Inertia misura quanto le newsletter sono lontane dal centro del loro gruppo, più è bassa più i gruppi sono compatti
    # Siccome decresce all'aumentare di k va letta cercando il gomito
    inertia.append(km.inertia_)

    # Silhouette va da -1 a 1. Su testo sparso i valori sono sempre bassi, quindi conta di più l'andamento relativo tra i k 
    sil = silhouette_score(X[campione], km.labels_[campione])
    silhouette.append(sil)
    print(f"k={k:3}  inertia={km.inertia_:12.1f}  silhouette={sil:.4f}")

# --- Grafici: gomito e silhouette
fig, ax = plt.subplots(1, 2, figsize=(11, 4))

ax[0].plot(K_DA_PROVARE, inertia, "o-", color="steelblue")
ax[0].set_xlabel("k (numero di cluster)"); ax[0].set_ylabel("Inertia")
ax[0].set_title("Metodo del gomito"); ax[0].axvline(K_SCELTO, color="crimson", linestyle="--", alpha=0.5)

ax[1].plot(K_DA_PROVARE, silhouette, "o-", color="seagreen")
ax[1].set_xlabel("k (numero di cluster)"); ax[1].set_ylabel("Silhouette score")
ax[1].set_title("Silhouette score (più alto = meglio)")
ax[1].axvline(K_SCELTO, color="crimson", linestyle="--", alpha=0.5)

plt.tight_layout(); plt.savefig(PLOT_OP / "scelta_k.png", dpi=150)
print("\nSalvato scelta_k.png (linea rossa tratteggiata = k usato nella pipeline)")