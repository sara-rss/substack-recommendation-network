"""ATTRIBUTI - Per ogni newsletter della rete scarico titolo e sottotitolo degli ultimi 10 post
(endpoint pubblico /api/v1/archive). Servono a ricavare il tema della newsletter.
Con checkpoint: se si interrompe, rilanciandolo riprende. Uscita: data/testi.jsonl"""
import sys, json, os, time, requests
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from comune import RACCOLTA, lista_nodi

OUT, STATO = RACCOLTA / "testi.jsonl", RACCOLTA / "stato_testi.json"
HEAD = {"User-Agent": "Mozilla/5.0 (ricerca accademica UniPi)", "Accept": "application/json"}

nodi = lista_nodi()
fatti = set(json.load(open(STATO))) if STATO.exists() else set()
print(f"{len(nodi)} newsletter, {len(fatti)} gia' scaricate")

f = open(OUT, "a")
try:
    for url in nodi:
        if url in fatti:
            continue
        try:
            r = requests.get(url + "/api/v1/archive?limit=10", headers=HEAD, timeout=15)
            post = r.json()
            rec = {"url": url,
                   "publication_id": post[0].get("publication_id") if post else None,
                   "n_post": len(post),
                   "testi": [{"titolo": p.get("title"), "sottotitolo": p.get("subtitle"),
                              "data": p.get("post_date")} for p in post]}
        except Exception as e:
            rec = {"url": url, "errore": str(e), "n_post": 0}
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        fatti.add(url)
        if len(fatti) % 100 == 0:
            f.flush(); os.fsync(f.fileno())
            json.dump(list(fatti), open(STATO, "w"))
            print(f"{len(fatti)}/{len(nodi)}")
        time.sleep(1)
finally:
    f.flush(); os.fsync(f.fileno()); f.close()
    json.dump(list(fatti), open(STATO, "w"))
    print(f"FINE: {len(fatti)} completati")
