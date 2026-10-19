"""PARTE 1 - Secondo tentativo sui nodi la cui richiesta era fallita durante il crawl
Aggiorna raccomandazioni_grezze.csv e stato_crawl.json."""
import sys, time, csv, json, os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from comune import RACCOLTA
from substack_api import Newsletter

STATO, ARCHI = RACCOLTA / "stato_crawl.json", RACCOLTA / "raccomandazioni_grezze.csv"
TENTATIVI, PAUSA = 3, 3   # tentativi per ogni nodo, secondi di attesa dopo un errore


# Normalizza l'url 
def sistema(url):
    u = url if url.startswith("http") else "https://" + url
    u = u.split("?")[0].split("#")[0].rstrip("/").lower()
    return u.replace("http://", "https://").replace("://www.", "://")


# Carico lo stato lasciato dal crawl e le sorgenti che hanno già archi nel CSV
s = json.load(open(STATO))
espansi, falliti = set(s["espansi"]), set(s.get("falliti", []))
gia_sorgenti = {riga[0] for riga in csv.reader(open(ARCHI, newline=""))}
print(f"Nodi falliti da riprovare: {len(falliti)}")

# Riprovo ogni nodo fallito 
# Gli archi di un nodo vengono aggiunti solo se non sono già nel CSV per evitare duplicati
recuperati, nuovi_archi = [], []
for url in sorted(falliti):
    for tentativo in range(TENTATIVI):
        try:
            archi = [(url, sistema(r.url)) for r in Newsletter(url).get_recommendations()]
            if url not in gia_sorgenti:
                nuovi_archi.extend(archi)
            recuperati.append(url)
            print(f"  ok   {url}  ({len(archi)} raccomandazioni)")
            break
        except Exception as e:
            if tentativo == TENTATIVI - 1:
                print(f"  KO   {url}  ({e})")
            time.sleep(PAUSA)
    time.sleep(1)

# Aggiungo i nuovi archi al CSV
with open(ARCHI, "a", newline="") as f:
    csv.writer(f).writerows(nuovi_archi)

# Aggiorno i recuperati da falliti a espansi
falliti -= set(recuperati)
espansi = (espansi | set(recuperati)) - falliti
s["espansi"], s["falliti"] = sorted(espansi), sorted(falliti)

# Salvo lo stato
tmp = str(STATO) + ".tmp"
json.dump(s, open(tmp, "w")); os.replace(tmp, STATO)

print(f"\nRecuperati: {len(recuperati)} | ancora falliti: {len(falliti)} "
      f"| nuovi archi: {len(nuovi_archi)}")
print("Ora rilancia 03_costruisci_rete.py")