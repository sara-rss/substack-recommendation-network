"""ATTRIBUTI 2/4 - Recupero dei nodi "deboli" (cluster marcati debole=si in nomi_cluster.csv) usando anche il
CORPO dei post (data/testi_extra.jsonl, scaricato da data_collection/05_scarica_corpo.py).

Come funziona (in modo deterministico, senza rifare KMeans):
 1. ricostruisco lo stesso spazio TF-IDF del clustering (titolo+sottotitolo);
 2. calcolo il centroide di ogni cluster come media dei suoi membri (da cluster_nodi.csv):
    e' esattamente il centroide che KMeans aveva trovato;
 3. assegno ogni nodo debole, descritto ora da titolo+sottotitolo+corpo, al centroide piu'
    vicino (il corpo e' piu' informativo dei soli titoli, quindi la nuova etichetta sostituisce
    la vecchia; riguarda solo nodi che erano deboli).
Uscita: data_collection/data/temi_finali.csv e plots/cluster_parole.csv"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import csv, json
import numpy as np
from collections import Counter
from comune import DATA, PLOT_OP, carica_titoli, vettorizzatore, carica_nomi_cluster

info = carica_nomi_cluster()
if any(not t for t, _, _ in info.values()):
    sys.exit("Compila prima data_collection/data/nomi_cluster.csv (tema, macro, debole per ogni cluster).")
nomi = {c: t for c, (t, _, _) in info.items()}
DEBOLI = {t for t, _, deb in info.values() if deb}
cluster = {u: int(c) for u, c in csv.reader(open(DATA / "cluster_nodi.csv"))}

# 1. stesso corpus e stesso TF-IDF del clustering
testi = carica_titoli()
urls = [u for u in testi if u in cluster]
doc = [testi[u] for u in urls]
vec = vettorizzatore()
X = vec.fit_transform(doc)
lab = np.array([cluster[u] for u in urls])

# 2. centroidi = media dei membri di ciascun cluster
ids = sorted(nomi)
C = np.vstack([np.asarray(X[lab == c].mean(axis=0)) for c in ids])


def piu_vicino(M):
    d2 = np.asarray(M.multiply(M).sum(axis=1)) - 2 * (M @ C.T) + (C * C).sum(axis=1)
    return [ids[i] for i in np.asarray(d2).argmin(axis=1)]


coerenti = np.mean(np.array(piu_vicino(X)) == lab)
print(f"Controllo: {100*coerenti:.2f}% dei nodi e' piu' vicino al centroide del proprio cluster")

parole = np.array(vec.get_feature_names_out())
with open(PLOT_OP / "cluster_parole.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["cluster", "nome", "n_nodi", "parole_caratteristiche"])
    for i, c in enumerate(ids):
        w.writerow([c, nomi[c], int((lab == c).sum()),
                    ", ".join(parole[C[i].argsort()[::-1][:15]])])

# 3. riclassifico i nodi deboli col corpo del testo
etichetta = {u: nomi[c] for u, c in cluster.items()}
nu, nd = [], []
for riga in open(DATA / "testi_extra.jsonl"):
    d = json.loads(riga)
    testo = " ".join(f"{x.get('titolo') or ''} {x.get('sottotitolo') or ''} {x.get('corpo') or ''}"
                     for x in d.get("testi", []))
    if d["url"] in etichetta and etichetta[d["url"]] in DEBOLI and len(testo.strip()) >= 20:
        nu.append(d["url"]); nd.append(testo)

cambi = Counter()
for u, c in zip(nu, piu_vicino(vec.transform(nd))):
    if nomi[c] not in DEBOLI:
        cambi[f"{etichetta[u]} -> {nomi[c]}"] += 1
    etichetta[u] = nomi[c]        # il corpo e' piu' informativo dei soli titoli: aggiorno sempre
print(f"\nNodi deboli riesaminati: {len(nu)} | recuperati a un tema vero: {sum(cambi.values())}")
for k, v in cambi.most_common(10):
    print(f"  {k:30} {v}")

with open(DATA / "temi_finali.csv", "w", newline="") as f:
    csv.writer(f).writerows(sorted(etichetta.items()))
c = Counter(etichetta.values()); tot = sum(c.values())
print("\n--- distribuzione dopo il recupero ---")
for t, n in c.most_common():
    print(f"  {t:15} {n:6} ({100*n/tot:.1f}%)")
