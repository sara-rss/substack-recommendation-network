"""PARTE 1 - Crawling delle raccomandazioni 
Parte da 15 newsletter seed e segue le raccomandazioni in ampiezza (BFS)
Salva un checkpoint ogni 100 nodi visitati"""
import sys, time, csv, json, os
from collections import deque
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from comune import SEED, RACCOLTA
from substack_api import Newsletter

STATO, ARCHI = RACCOLTA / "stato_crawl.json", RACCOLTA / "raccomandazioni_grezze.csv"
MAX, PAUSA, CHECKPOINT = 20000, 1, 100   # max nodi espansi, secondi tra due richieste, nodi tra due salvataggi


# Normalizza l'url così che la stessa newsletter abbia sempre lo stesso nome
def sistema(url):
    u = url if url.startswith("http") else "https://" + url
    u = u.split("?")[0].split("#")[0].rstrip("/").lower()
    return u.replace("http://", "https://").replace("://www.", "://")


seed = [sistema(u) for u in SEED]   # 15 seed, 3 per area (definiti in comune.py)

# Se esiste un checkpoint riprendo da lì, altrimenti parto dai seed
# coda = nodi da visitare, noti = nodi già scoperti, espansi = nodi scaricati, falliti = richieste non riuscite
if STATO.exists():
    s = json.load(open(STATO))
    coda, noti = deque(s["coda"]), set(s["noti"])
    espansi, falliti = set(s["espansi"]), set(s.get("falliti", []))
    print(f"Ripresa da {len(espansi)} espansi, {len(noti)} noti, {len(falliti)} falliti")
else:
    coda, noti, espansi, falliti = deque(seed), set(seed), set(), set()


# Aggiunge gli archi nuovi al CSV e salva lo stato del crawl
# Lo stato viene scritto prima su un file temporaneo e poi rinominato:
# se lo script si interrompe durante la scrittura, il checkpoint precedente resta integro
def salva(buffer):
    if buffer:
        with open(ARCHI, "a", newline="") as f:
            csv.writer(f).writerows(buffer)
            f.flush(); os.fsync(f.fileno())
    tmp = str(STATO) + ".tmp"
    with open(tmp, "w") as f:
        json.dump({"coda": list(coda), "noti": list(noti),
                   "espansi": list(espansi), "falliti": list(falliti)}, f)
        f.flush(); os.fsync(f.fileno())
    os.replace(tmp, STATO)


# Scarica le raccomandazioni di url, mette in coda le newsletter mai viste
# e aggiunge gli archi al buffer. Restituisce True se la richiesta è riuscita
def espandi(url, buffer):
    try:
        archi = [(url, sistema(r.url)) for r in Newsletter(url).get_recommendations()]
    except Exception as e:
        print("errore:", url, e)
        return False
    for _, t in archi:
        if t not in noti:
            noti.add(t); coda.append(t)
    buffer.extend(archi)
    return True


# Ciclo principale: un nodo è espanso solo se la richiesta riesce, altrimenti finisce tra i falliti.
buffer, visitati = [], 0
try:
    while coda and len(espansi) < MAX:
        url = coda.popleft()
        if url in espansi or url in falliti:
            continue
        if espandi(url, buffer):
            espansi.add(url)
        else:
            falliti.add(url)
        visitati += 1
        if visitati % CHECKPOINT == 0:
            salva(buffer); buffer = []
            print(f"{len(espansi)} espansi | {len(noti)} noti | "
                  f"{len(coda)} in coda | {len(falliti)} falliti")
        time.sleep(PAUSA)
finally:
    salva(buffer)
    print(f"\nFINE: {len(espansi)} espansi, {len(noti)} noti, {len(falliti)} falliti "
          f"(per riprovarli: 02_riprova_falliti.py)")