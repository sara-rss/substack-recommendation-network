"""Recupero dei nodi deboli

Alcuni cluster sono deboli, i soli titoli non bastano a capire di che argomento parlano
Per le newsletter di questi cluster provo a usare anche il testo completo di alcuni post

Ricostruisco gli stessi numeri usati nel clustering, calcolo il centro di ogni gruppo e sposto 
ogni newsletter debole nel gruppo il cui centro è più vicino al suo testo completo"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import csv, json
import numpy as np
from collections import Counter
from comune import RACCOLTA, ELAB, PLOT_OP, carica_titoli, vettorizzatore, carica_nomi_cluster

# --- Carico le informazioni sui cluster ---

# Viene letto nomi_cluster.csv (compilato a mano), dove per ogni cluster ci sono tema, macro-area e se è debole
info = carica_nomi_cluster()


nomi = {c: t for c, (t, _, _) in info.items()} # Dizionario {numero del cluster: nome del tema}

DEBOLI = {t for t, _, deb in info.values() if deb} # Insieme dei temi deboli

# Legge in quale cluster è finita ogni newsletter: dizionario {url: numero del cluster}
cluster = {u: int(c) for u, c in csv.reader(open(ELAB / "cluster_nodi.csv"))}

# --- Ricostruisco gli stessi numeri usati nel clustering ---

# Prendo le stesse newsletter dello script di clustering e le trasformo in numeri con lo stesso vettorizzatore
testi = carica_titoli()
urls = [u for u in testi if u in cluster]
doc = [testi[u] for u in urls]
vec = vettorizzatore()
X = vec.fit_transform(doc)

# Il cluster di ogni newsletter
lab = np.array([cluster[u] for u in urls])

# --- Calcolo il centro di ogni cluster ---

# Il centro di un gruppo è la media di tutte le newsletter che ne fanno parte
ids = sorted(nomi)
C = np.vstack([np.asarray(X[lab == c].mean(axis=0)) for c in ids])


def piu_vicino(M):
    """Per ogni riga di M (una newsletter trasformata in numeri) restituisce
    il numero del cluster il cui centro è più vicino"""
    # Calcola la distanza (al quadrato) tra ogni newsletter e ogni centro
    d2 = np.asarray(M.multiply(M).sum(axis=1)) - 2 * (M @ C.T) + (C * C).sum(axis=1)
    # argmin trova, per ogni newsletter, la posizione del centro con la distanza più piccola
    return [ids[i] for i in np.asarray(d2).argmin(axis=1)]


# Controllo che la ricostruzione sia giusta
coerenti = np.mean(np.array(piu_vicino(X)) == lab)
print(f"Controllo: {100*coerenti:.2f}% dei nodi è più vicino al centroide del proprio cluster")

# Riscrivo cluster_parole.csv aggiungendo il nome del tema accanto al numero del cluster.
parole = np.array(vec.get_feature_names_out())
with open(PLOT_OP / "cluster_parole.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["cluster", "nome", "n_nodi", "parole_caratteristiche"])
    for i, c in enumerate(ids):
        w.writerow([c, nomi[c], int((lab == c).sum()),
                    ", ".join(parole[C[i].argsort()[::-1][:15]])])   # le 15 parole più importanti del centro

# --- Riassegno le newsletter deboli usando il testo completo ---

# Parto dal tema assegnato dal clustering: dizionario {url: nome del tema}
etichetta = {u: nomi[c] for u, c in cluster.items()}

# Leggo il file con i testi completi dei post
nu, nd = [], []   # nu = url delle newsletter da riesaminare, nd = il loro testo completo
for riga in open(RACCOLTA / "testi_extra.jsonl"):
    d = json.loads(riga)
    # Unisco titolo, sottotitolo e corpo di tutti i post della newsletter in un unico testo
    testo = " ".join(f"{x.get('titolo') or ''} {x.get('sottotitolo') or ''} {x.get('corpo') or ''}"
                     for x in d.get("testi", []))
    # Tengo la newsletter solo se ha un cluster, il suo tema è debole e il testo ha almeno 20 caratteri
    if d["url"] in etichetta and etichetta[d["url"]] in DEBOLI and len(testo.strip()) >= 20:
        nu.append(d["url"]); nd.append(testo)

# Trasformo i testi completi in numeri (con lo stesso vocabolario di prima) e trovo il centro più vicino
# Conto quante newsletter passano da un tema debole a un tema vero
cambi = Counter()
for u, c in zip(nu, piu_vicino(vec.transform(nd))):
    if nomi[c] not in DEBOLI:
        cambi[f"{etichetta[u]} -> {nomi[c]}"] += 1
    etichetta[u] = nomi[c]

print(f"\nNodi deboli riesaminati: {len(nu)} | recuperati a un tema vero: {sum(cambi.values())}")
# Stampo i 10 spostamenti più frequenti (da quale tema debole a quale tema vero)
for k, v in cambi.most_common(10):
    print(f"  {k:30} {v}")

# Per ogni newsletter salvo il tema definitivo (dopo il recupero)
with open(ELAB / "temi_finali.csv", "w", newline="") as f:
    csv.writer(f).writerows(sorted(etichetta.items()))

# Stampo quante newsletter ci sono per ogni tema
c = Counter(etichetta.values()); tot = sum(c.values())
print("\n--- distribuzione dopo il recupero ---")
for t, n in c.most_common():
    print(f"  {t:15} {n:6} ({100*n/tot:.1f}%)")