"""PARTE 1 - Crawling a palla di neve (snowball) delle raccomandazioni Substack.
Parte da 15 newsletter seed e segue le raccomandazioni in ampiezza (BFS).
Salva un checkpoint ogni 100 nodi: se si interrompe, rilanciandolo riprende da dove era.
Uscita: data/archi.csv (archi diretti) e data/stato.json (stato del crawl)."""
import sys, time, csv, json, os
from collections import deque
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from comune import DATA
from substack_api import Newsletter

STATO, ARCHI = DATA / "stato.json", DATA / "archi.csv"
MAX, PAUSA, CHECKPOINT = 20000, 1, 100


def sistema(url):
    """Normalizza l'URL cosi' che la stessa newsletter abbia sempre lo stesso nome."""
    u = url if url.startswith("http") else "https://" + url
    u = u.split("?")[0].split("#")[0].rstrip("/").lower()
    return u.replace("http://", "https://").replace("://www.", "://")


seed = [sistema(u) for u in [
    "https://georgesaunders.substack.com",
    "https://footnotesandtangents.substack.com",
    "https://pandorasykes.substack.com",          # letteratura
    "https://greenwald.substack.com",
    "https://samf.substack.com",
    "https://chrishedges.substack.com",           # politica
    "https://natesnewsletter.substack.com",
    "https://newsletter.pragmaticengineer.com",
    "https://damnang2.substack.com",              # tecnologia
    "https://michaeljburry.substack.com",
    "https://capitalwars.substack.com",
    "https://charliepgarcia.substack.com",        # finanza
    "https://yourlocalepidemiologist.substack.com",
    "https://theskepticalcardiologist.substack.com",
    "https://theunbiasedscipod.substack.com",     # scienza
]]

if STATO.exists():
    s = json.load(open(STATO))
    coda, noti = deque(s["coda"]), set(s["noti"])
    espansi, falliti = set(s["espansi"]), set(s.get("falliti", []))
    print(f"Ripresa da {len(espansi)} espansi, {len(noti)} noti, {len(falliti)} falliti")
else:
    coda, noti, espansi, falliti = deque(seed), set(seed), set(), set()


def salva(buffer):
    if buffer:
        with open(ARCHI, "a", newline="") as f:
            csv.writer(f).writerows(buffer)
            f.flush(); os.fsync(f.fileno())
    tmp = str(STATO) + ".tmp"            # scrittura sicura: file temporaneo + rinomina
    with open(tmp, "w") as f:
        json.dump({"coda": list(coda), "noti": list(noti),
                   "espansi": list(espansi), "falliti": list(falliti)}, f)
        f.flush(); os.fsync(f.fileno())
    os.replace(tmp, STATO)


def espandi(url, buffer):
    """Scarica le raccomandazioni di `url`. True se la richiesta e' riuscita."""
    try:
        archi = [(url, sistema(r.url)) for r in Newsletter(url).get_recommendations()]
    except Exception as e:
        print("errore:", url, e)
        return False
    for _, t in archi:                    # aggiungo gli archi solo a richiesta riuscita
        if t not in noti:
            noti.add(t); coda.append(t)
    buffer.extend(archi)
    return True


buffer, visitati = [], 0
try:
    while coda and len(espansi) < MAX:
        url = coda.popleft()
        if url in espansi or url in falliti:
            continue
        # CORREZIONE: un nodo e' "espanso" SOLO se la richiesta e' andata a buon fine;
        # altrimenti finisce tra i falliti (prima veniva contato comunque come espanso).
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
