"""ATTRIBUTI 1/4 - Lingua + clustering tematico.
 1. Rilevo la LINGUA di ogni newsletter (langdetect) -> data_collection/data/elaborazione/lingua_nodi.csv.
    Le newsletter non in inglese NON entrano nel clustering: con un TF-IDF pensato per l'inglese
    finirebbero raggruppate per lingua ("spagnolo", "portoghese") e non per tema. La lingua
    diventa un attributo a parte del nodo.
 2. TF-IDF + KMeans (k=16) su titolo+sottotitolo delle newsletter in inglese, ignorando
    numeri, date, mesi e parole di servizio (vedi comune.vettorizzatore).
Uscita: data_collection/data/elaborazione/cluster_nodi.csv, plots/cluster_parole.csv e un modello vuoto di
data_collection/data/elaborazione/nomi_cluster.csv DA COMPILARE A MANO (tema, macro, debole) guardando le parole.

ATTENZIONE - passo eseguito UNA VOLTA SOLA. KMeans non da' gli stessi cluster su versioni diverse
di scikit-learn, anche a seed fissato: il risultato e' "congelato" in cluster_nodi.csv e gli script
successivi lo leggono senza rifare il clustering. Lo script non sovrascrive un cluster_nodi.csv
esistente a meno di usare --forza (in quel caso nomi_cluster.csv viene azzerato e va ricompilato)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import csv
import numpy as np
from collections import Counter
from sklearn.cluster import KMeans
from langdetect import detect, DetectorFactory
from comune import ELAB, PLOT_OP, carica_titoli, vettorizzatore

K = 16   # scelto come il k piu' piccolo per cui le 5 aree dei seed emergono come cluster distinti
if (ELAB / "cluster_nodi.csv").exists() and "--forza" not in sys.argv:
    sys.exit("cluster_nodi.csv esiste gia': clustering congelato (vedi intestazione). "
             "Usa --forza per rifarlo.")

testi = carica_titoli()
print(f"Newsletter con testo sufficiente: {len(testi)}")

DetectorFactory.seed = 0                      # langdetect e' casuale: fisso il seed
lingua = {}
for u, t in testi.items():
    try:
        lingua[u] = detect(t)
    except Exception:
        lingua[u] = "?"
with open(ELAB / "lingua_nodi.csv", "w", newline="") as f:
    csv.writer(f).writerows(sorted(lingua.items()))
c = Counter(lingua.values())
print("Lingue:", ", ".join(f"{l} {n}" for l, n in c.most_common(8)),
      f"| non inglesi: {len(lingua) - c['en']} ({100*(1 - c['en']/len(lingua)):.1f}%)")

urls = [u for u in testi if lingua[u] == "en"]
vec = vettorizzatore()
X = vec.fit_transform([testi[u] for u in urls])
km = KMeans(n_clusters=K, random_state=42, n_init=10).fit(X)

with open(ELAB / "cluster_nodi.csv", "w", newline="") as f:
    csv.writer(f).writerows(zip(urls, km.labels_))
parole = np.array(vec.get_feature_names_out())
with open(PLOT_OP / "cluster_parole.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["cluster", "n_nodi", "parole_caratteristiche"])
    for k in range(K):
        top = ", ".join(parole[km.cluster_centers_[k].argsort()[::-1][:15]])
        w.writerow([k, int((km.labels_ == k).sum()), top])
        print(f"cluster {k:2} ({(km.labels_ == k).sum():5} nodi): {top}")

nomi = ELAB / "nomi_cluster.csv"
with open(nomi, "w", newline="") as f:
    w = csv.writer(f); w.writerow(["cluster", "tema", "macro", "debole"])
    w.writerows([k, "", "", ""] for k in range(K))
print("""
ORA compila data_collection/data/elaborazione/nomi_cluster.csv, una riga per cluster:
  tema   = nome breve del tema (es. equity, food, writing, generic...)
  macro  = una tra: finance, business, technology, politics, science_health, arts_letters,
           food, lifestyle_culture, unlabeled   (unlabeled = il cluster non e' un vero tema)
  debole = si / no. 'si' per i cluster vaghi (generico, vita quotidiana, 'coming soon'...):
           per questi nodi si scarica anche il corpo dei post e si ritenta la classificazione.""")
