"""Le newsletter vengono suddivise in cluster in base all'argomento
Prima riconosce la lingua di ogni newsletter, poi tiene solo quelle in inglese
e le divide in 16 gruppi con KMeans"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import csv
import numpy as np
from collections import Counter
from sklearn.cluster import KMeans
from langdetect import detect, DetectorFactory
from comune import ELAB, PLOT_OP, carica_titoli, vettorizzatore

# Dopo alcune prove, anche manuali, è stato scelto 16 perché è il numero più piccolo con cui
# le 5 aree tematiche dei seed escono come gruppi separati, in particolare health (che con 15 non si divideva)
K = 16

# Se i gruppi sono già stati calcolati (si trovano in cluster_nodi) lo script si ferma per non sovrascriverli.
if (ELAB / "cluster_nodi.csv").exists() and "--forza" not in sys.argv:
    sys.exit("cluster_nodi.csv esiste già: clustering congelato (vedi intestazione). "
             "Usa --forza per rifarlo.")

# Carico i testi delle newsletter: un dizionario {url: testo}
testi = carica_titoli()
print(f"Newsletter con testo sufficiente: {len(testi)}")

# --- Riconosco la lingua di ogni newsletter ---

# Fisso il seed per ottenere sempre lo stesso risultato ogni volta che rilancio lo script
DetectorFactory.seed = 0

lingua = {}
for u, t in testi.items():
    try:
        lingua[u] = detect(t)   # Restituisce la lingua come "en", "it", "de"
    except Exception:
        lingua[u] = "?"         # Se il testo non basta per capire la lingua mette ?

# Salvo la lingua di ogni newsletter in un file, così gli altri script possono usarla
with open(ELAB / "lingua_nodi.csv", "w", newline="") as f:
    csv.writer(f).writerows(sorted(lingua.items()))

# Conto quante newsletter ci sono per ogni lingua e stampo le 8 più frequenti + il numero e la percentuale di quelle non in inglese
c = Counter(lingua.values())
print("Lingue:", ", ".join(f"{l} {n}" for l, n in c.most_common(8)),
      f"| non inglesi: {len(lingua) - c['en']} ({100*(1 - c['en']/len(lingua)):.1f}%)")

# --- Divido le newsletter in inglese in gruppi ---

# Tengo solo le newsletter in inglese
urls = [u for u in testi if lingua[u] == "en"]

vec = vettorizzatore()
X = vec.fit_transform([testi[u] for u in urls])


km = KMeans(n_clusters=K, random_state=42, n_init=10).fit(X)

# --- Salvo i risultati ---

# Per ogni newsletter salvo il numero del gruppo in cui è finita (da 0 a 15)
with open(ELAB / "cluster_nodi.csv", "w", newline="") as f:
    csv.writer(f).writerows(zip(urls, km.labels_))

# Recupero l'elenco delle parole del vocabolario, nello stesso ordine delle colonne di X
parole = np.array(vec.get_feature_names_out())

# Per ogni gruppo trovo le 15 parole più importanti per capire di che argomento parla ogni gruppo
with open(PLOT_OP / "cluster_parole.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["cluster", "n_nodi", "parole_caratteristiche"])
    for k in range(K):
        top = ", ".join(parole[km.cluster_centers_[k].argsort()[::-1][:15]])
        w.writerow([k, int((km.labels_ == k).sum()), top])   # Numero del gruppo, quante newsletter contiene, parole
        print(f"cluster {k:2} ({(km.labels_ == k).sum():5} nodi): {top}")

# Crea un file vuoto da compilare a mano: per ogni gruppo andranno scritti il tema, la macro-area a cui appartiene e se è un gruppo debole
nomi = ELAB / "nomi_cluster.csv"
with open(nomi, "w", newline="") as f:
    w = csv.writer(f); w.writerow(["cluster", "tema", "macro", "debole"])
    w.writerows([k, "", "", ""] for k in range(K))