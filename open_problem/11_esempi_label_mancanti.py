"""Esempi concreti di newsletter senza label (tema non ricavabile dal testo): i titoli dei loro
ultimi post e la comunita' in cui Louvain le colloca, con il tema dominante di quella comunita'.
Solo illustrativo: non assegna nessuna label."""
import sys, json, random
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from collections import Counter, defaultdict
from comune import DATA, carica_grafo, carica_attributi, carica_comunita, corto

N_ESEMPI, MIN_PUREZZA = 6, 0.6
CASI_NOTI = ["100xfarm", "5mwpress", "10am.pro"]

G = carica_grafo(); tema, macro = carica_attributi(); com = carica_comunita()
titoli = {}
for riga in open(DATA / "testi.jsonl"):
    d = json.loads(riga)
    titoli[d["url"]] = [x.get("titolo") or "" for x in d.get("testi", []) if x.get("titolo")]
senza = {u for u in G if macro.get(u, "unlabeled") == "unlabeled"}
conta = defaultdict(Counter)
for u in G:
    if u not in senza:
        conta[com[u]][macro[u]] += 1


def dominante(c):
    if not conta[c]:                     # comunita' minuscola senza nodi con label
        return "nessuno", 0.0
    t, n = conta[c].most_common(1)[0]
    return t, n / sum(conta[c].values())


def mostra(u):
    t, p = dominante(com[u])
    print(f"\n■ {corto(u)}   (label dal testo: {tema.get(u, 'nessun testo')})")
    for x in titoli.get(u, [])[:4]:
        print(f"     · {x[:90]}")
    print(f"  comunita' {com[u]}: tema dominante {t.upper()} ({100*p:.0f}% dei nodi con label)")


print("=== CASI DI STUDIO ===")
for k in CASI_NOTI:
    for u in G:
        if k in u:
            mostra(u)
print(f"\n\n=== ESEMPI A CASO (in comunita' con tema dominante >= {int(100*MIN_PUREZZA)}%) ===")
cand = [u for u in senza if titoli.get(u) and dominante(com[u])[1] >= MIN_PUREZZA]
random.seed(int(sys.argv[1]) if len(sys.argv) > 1 else 1)
for u in random.sample(cand, min(N_ESEMPI, len(cand))):
    mostra(u)
print("\n(Per altri esempi: python esempi_nodi_deboli.py 2, 3, ...)")
