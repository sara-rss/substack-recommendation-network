"""ATTRIBUTI - Secondo giro di scraping: per i nodi finiti in cluster "deboli"
(debole=si in nomi_cluster.csv) scarico anche l'inizio del CORPO dei post,
per avere piu' testo su cui classificarli. Va lanciato dopo open_problem/01_clustering_temi.py.
Uscita: data/testi_extra.jsonl"""
import sys, json, csv, os, time, requests
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from comune import RACCOLTA, ELAB, carica_nomi_cluster

OUT, STATO = RACCOLTA / "testi_extra.jsonl", RACCOLTA / "stato_extra.json"
HEAD = {"User-Agent": "Mozilla/5.0 (ricerca accademica UniPi)", "Accept": "application/json"}
# cluster deboli = quelli marcati debole=si in data_collection/data/elaborazione/nomi_cluster.csv
deboli = {c for c, (_, _, deb) in carica_nomi_cluster().items() if deb}
da_rifare = [u for u, c in csv.reader(open(ELAB / "cluster_nodi.csv")) if int(c) in deboli]


fatti = set(json.load(open(STATO))) if STATO.exists() else set()
mancanti = [u for u in da_rifare if u not in fatti]
print(f"{len(da_rifare)} nodi deboli, di cui {len(mancanti)} ancora da scaricare")
f = open(OUT, "a")
try:
    for i, url in enumerate(mancanti, 1):
        try:
            r = requests.get(url + "/api/v1/archive?limit=10", headers=HEAD, timeout=15)
            post = r.json() if r.status_code == 200 else []
            rec = {"url": url, "testi": [
                {"titolo": p.get("title"), "sottotitolo": p.get("subtitle"),
                 "corpo": p.get("truncated_body_text")} for p in post]}
        except Exception as e:
            rec = {"url": url, "errore": str(e), "testi": []}
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        fatti.add(url)
        if i % 100 == 0:
            f.flush(); os.fsync(f.fileno())
            json.dump(list(fatti), open(STATO, "w"))
            print(f"{i}/{len(mancanti)}")
        time.sleep(1)
finally:
    f.flush(); os.fsync(f.fileno()); f.close()
    json.dump(list(fatti), open(STATO, "w"))
    print(f"FINE: scaricati {len(mancanti)} nodi nuovi")
