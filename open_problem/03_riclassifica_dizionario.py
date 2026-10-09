"""ATTRIBUTI 3/4 - Ultimo recupero dei nodi ancora deboli con un dizionario di parole chiave
NON ambigue, applicato a titolo+sottotitolo+corpo. Regole prudenziali: almeno l'1% delle parole
deve essere tematico e il primo tema deve battere il secondo di almeno 1.5 volte; altrimenti
il nodo resta com'e'. Poi associa a ogni tema la sua macro-categoria (da nomi_cluster.csv).
Legge data_collection/data/elaborazione/temi_finali.csv (mai modificato) e scrive data_collection/data/elaborazione/attributi_nodi.csv:
si puo' rilanciare quante volte si vuole, il risultato e' sempre lo stesso."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import csv, json, re
from collections import Counter
from comune import lista_nodi, RACCOLTA, ELAB, carica_nomi_cluster, carica_lingue

info = carica_nomi_cluster()
MACRO = {t: m for t, m, _ in info.values()}            # tema -> macro (da nomi_cluster.csv)
DEBOLI = {t for t, _, deb in info.values() if deb}
# macro dei temi del dizionario (servono anche se un tema non esiste come cluster)
MACRO_DIZ = {"equity": "finance", "macro_finance": "finance", "business": "business",
             "ai_tech": "technology", "ai_coding": "technology", "geopolitics": "politics",
             "health": "science_health", "writing": "arts_letters", "food": "food"}

# solo parole INEQUIVOCABILI (niente termini generici come "growth", "reading", "policy"...)
DIZ = {
 "equity": """stock stocks portfolio earnings valuation dividend dividends shares ticker
   nasdaq ipo shareholder shareholders equities smallcap midcap bagger baggers compounder
   compounders moat undervalued overvalued buyback buybacks screener""",
 "macro_finance": """fed inflation macro bond bonds yield yields treasury treasuries gdp
   recession bitcoin crypto ethereum commodities forex liquidity monetary hawkish dovish
   stagflation macroeconomic""",
 "business": """startup startups founder founders saas marketing branding b2b
   entrepreneurship entrepreneur freelance monetize monetization churn ecommerce funnel
   bootstrapped solopreneur""",
 "ai_tech": """ai openai llm llms gpt chatgpt anthropic neural chatbot chatbots robotics
   semiconductor semiconductors agi genai""",
 "ai_coding": """coding programming developer developers python javascript github backend
   frontend devops kubernetes sql refactoring debugging typescript""",
 "geopolitics": """geopolitics geopolitical ukraine russia iran israel gaza nato election
   elections congress senate democrats republicans trump biden diplomacy sanctions
   parliament legislation immigration""",
 "health": """medical medicine doctor doctors patients cancer vaccine vaccines clinical
   psychiatry nutrition diabetes cardiology neuroscience epidemiology hospital diagnosis
   symptoms""",
 "writing": """novel novels fiction poetry poem poems literary literature author authors
   manuscript publishing memoir essay essays prose storytelling bookclub""",
 "food": """recipe recipes cooking baking kitchen ingredients pasta sourdough cuisine chef
   restaurant restaurants cocktail cocktails roasted braised dessert vegetarian""",
}
DIZ = {t: set(w.split()) for t, w in DIZ.items()}
SOGLIA, MARGINE, MIN_PAROLE = 0.010, 1.5, 30


def punteggia(testo):
    parole = re.findall(r"[a-z]+", testo.lower())
    if len(parole) < MIN_PAROLE:
        return None                                   # troppo poco testo
    score = {t: sum(w in v for w in parole) / len(parole) for t, v in DIZ.items()}
    primo, secondo = sorted(score.values(), reverse=True)[:2]
    if primo < SOGLIA:
        return None                                   # evidenza insufficiente
    if secondo > 0 and primo / secondo < MARGINE:
        return None                                   # ambiguo tra due temi
    return max(score, key=score.get)


tema = dict(csv.reader(open(ELAB / "temi_finali.csv")))
cambi = Counter()
for riga in open(RACCOLTA / "testi_extra.jsonl"):
    d = json.loads(riga)
    u = d["url"]
    if tema.get(u) not in DEBOLI:
        continue
    testo = " ".join(f"{t.get('titolo') or ''} {t.get('sottotitolo') or ''} {t.get('corpo') or ''}"
                     for t in d.get("testi", []))
    nuovo = punteggia(testo)
    if nuovo:
        cambi[f"{tema[u]} -> {nuovo}"] += 1
        tema[u] = nuovo

print(f"Riassegnati dal dizionario: {sum(cambi.values())} nodi")
for k, v in cambi.most_common(12):
    print(f"  {k:30} {v}")

# le newsletter non in inglese: tema "non_english", nessuna macro (la lingua e' in lingua_nodi.csv)
for u, l in carica_lingue().items():
    if l != "en":
        tema[u] = "non_english"
MACRO = {**MACRO_DIZ, **MACRO, "non_english": "unlabeled"}
righe = [(u, t, MACRO[t]) for u, t in sorted(tema.items())]
with open(ELAB / "attributi_nodi.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["url", "tema", "macro"]); w.writerows(righe)

n_rete = len(lista_nodi())
for titolo, col in [("TEMI FINI", 1), ("MACRO-CATEGORIE", 2)]:
    print(f"\n=== {titolo} (su {len(righe)} nodi con testo) ===")
    c = Counter(r[col] for r in righe)
    for t, n in c.most_common():
        print(f"  {t:18} {n:6} ({100*n/len(righe):.1f}%)")
utili = sum(r[2] != "unlabeled" for r in righe)
print(f"\nNodi della rete: {n_rete} | con testo: {len(righe)} | senza testo: {n_rete - len(righe)}")
print(f"Nodi con tema utilizzabile: {utili} ({100*utili/n_rete:.1f}% della rete)")
