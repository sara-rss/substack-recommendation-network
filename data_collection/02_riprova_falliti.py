"""PARTE 1 - Secondo tentativo sui nodi la cui richiesta era fallita durante il crawl
(interruzione di connettivita'). Chi riesce passa tra gli espansi e i suoi archi vengono
aggiunti a raccomandazioni_grezze.csv; chi fallisce ancora resta tra i falliti e verra' ESCLUSO dalla
rete finale da 03_costruisci_rete.py (non avremmo dati completi su di lui)."""
import sys, time, csv, json, os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from comune import RACCOLTA
from substack_api import Newsletter

STATO, ARCHI = RACCOLTA / "stato_crawl.json", RACCOLTA / "raccomandazioni_grezze.csv"
TENTATIVI, PAUSA = 3, 3


def sistema(url):
    u = url if url.startswith("http") else "https://" + url
    u = u.split("?")[0].split("#")[0].rstrip("/").lower()
    return u.replace("http://", "https://").replace("://www.", "://")


s = json.load(open(STATO))
espansi, falliti = set(s["espansi"]), set(s.get("falliti", []))
gia_sorgenti = {riga[0] for riga in csv.reader(open(ARCHI, newline=""))}
print(f"Nodi falliti da riprovare: {len(falliti)}")

recuperati, nuovi_archi = [], []
for url in sorted(falliti):
    for tentativo in range(TENTATIVI):
        try:
            archi = [(url, sistema(r.url)) for r in Newsletter(url).get_recommendations()]
            if url not in gia_sorgenti:          # evito duplicati se rilanciato
                nuovi_archi.extend(archi)
            recuperati.append(url)
            print(f"  ok   {url}  ({len(archi)} raccomandazioni)")
            break
        except Exception as e:
            if tentativo == TENTATIVI - 1:
                print(f"  KO   {url}  ({e})")
            time.sleep(PAUSA)
    time.sleep(1)

with open(ARCHI, "a", newline="") as f:
    csv.writer(f).writerows(nuovi_archi)
falliti -= set(recuperati)
espansi = (espansi | set(recuperati)) - falliti   # i falliti non sono mai "espansi"
s["espansi"], s["falliti"] = sorted(espansi), sorted(falliti)
tmp = str(STATO) + ".tmp"
json.dump(s, open(tmp, "w")); os.replace(tmp, STATO)

print(f"\nRecuperati: {len(recuperati)} | ancora falliti: {len(falliti)} "
      f"| nuovi archi: {len(nuovi_archi)}")
print("Ora rilancia 03_costruisci_rete.py")
