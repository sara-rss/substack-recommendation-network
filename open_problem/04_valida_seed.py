"""ATTRIBUTI 4/4 - Validazione: i 15 seed hanno una categoria nota (scelta a mano).
Controllo se la classificazione automatica li mette nella macro-categoria giusta."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from comune import carica_attributi, corto, SEED_PER_AREA

ATTESO = {u: area for area, lista in SEED_PER_AREA.items() for u in lista}
tema, macro = carica_attributi()
ok = 0
for u, att in ATTESO.items():
    giusto = macro.get(u) == att
    ok += giusto
    print(f"  {'OK ' if giusto else 'NO '} {corto(u):35} atteso {att:15} -> {macro.get(u, 'senza testo')} ({tema.get(u, '-')})")
print(f"\nCorretti: {ok}/15")
