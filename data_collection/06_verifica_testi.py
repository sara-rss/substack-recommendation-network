"""Controllo di copertura dei testi scaricati (quante newsletter hanno almeno un post)."""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from comune import DATA

tot = con_testo = senza = errori = 0
distribuzione = {}

for riga in open(DATA / "testi.jsonl"):
    d = json.loads(riga)
    tot += 1
    n = d.get("n_post", 0)
    distribuzione[n] = distribuzione.get(n, 0) + 1
    if d.get("errore"):
        errori += 1
    elif n > 0:
        con_testo += 1
    else:
        senza += 1

print(f"Righe totali: {tot}")
print(f"Con almeno un post: {con_testo} ({100*con_testo/tot:.1f}%)")
print(f"Senza post: {senza}")
print(f"Con errore: {errori}")
print("\nQuanti post per newsletter:")
for n in sorted(distribuzione):
    print(f"  {n} post -> {distribuzione[n]} newsletter")