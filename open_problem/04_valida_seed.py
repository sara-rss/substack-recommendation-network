"""ATTRIBUTI 4/4 - Validazione: i 15 seed hanno una categoria nota (scelta a mano).
Controllo se la classificazione automatica li mette nella macro-categoria giusta."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from comune import carica_attributi, corto

ATTESO = {
    "https://georgesaunders.substack.com": "arts_letters",
    "https://footnotesandtangents.substack.com": "arts_letters",
    "https://pandorasykes.substack.com": "arts_letters",
    "https://greenwald.substack.com": "politics",
    "https://samf.substack.com": "politics",
    "https://chrishedges.substack.com": "politics",
    "https://natesnewsletter.substack.com": "technology",
    "https://newsletter.pragmaticengineer.com": "technology",
    "https://damnang2.substack.com": "technology",
    "https://michaeljburry.substack.com": "finance",
    "https://capitalwars.substack.com": "finance",
    "https://charliepgarcia.substack.com": "finance",
    "https://yourlocalepidemiologist.substack.com": "science_health",
    "https://theskepticalcardiologist.substack.com": "science_health",
    "https://theunbiasedscipod.substack.com": "science_health",
}
tema, macro = carica_attributi()
ok = 0
for u, att in ATTESO.items():
    giusto = macro.get(u) == att
    ok += giusto
    print(f"  {'OK ' if giusto else 'NO '} {corto(u):35} atteso {att:15} -> {macro.get(u, 'senza testo')} ({tema.get(u, '-')})")
print(f"\nCorretti: {ok}/15")
