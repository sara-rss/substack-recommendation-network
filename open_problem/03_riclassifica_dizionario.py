"""Ultimo recupero delle newsletter ancora deboli con dizionario di parole chiave

Per ogni tema ho scelto a mano un elenco di parole inerenti a quel tema 
Cerco queste parole nel testo completo della newsletter e la sposto in un tema solo se sono
rispettate due regole:
  - almeno l'1% delle parole del testo deve appartenere al dizionario di un tema;
  - il tema con più parole deve averne almeno 1.5 volte quelle del secondo.

Poi associa a ogni tema la sua macro-categoria """

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import csv, json, re
from collections import Counter
from comune import lista_nodi, RACCOLTA, ELAB, carica_nomi_cluster, carica_lingue

# --- Carico le informazioni sui cluster (da nomi_cluster, quello compilato a mano) ---

info = carica_nomi_cluster()

MACRO = {t: m for t, m, _ in info.values()} # Dizionario {tema: macro-categoria}

DEBOLI = {t for t, _, deb in info.values() if deb} # Insieme dei temi deboli

# Macro-categorie dei temi del dizionario qui sotto, perché un tema del dizionario potrebbe non esistere come cluster
MACRO_DIZ = {"equity": "finance", "macro_finance": "finance", "business": "business",
             "ai_tech": "technology", "ai_coding": "technology", "geopolitics": "politics",
             "health": "science_health", "writing": "arts_letters", "food": "food"}

# --- Dizionario delle parole chiave ---

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
 "geopolitics": """geopolitics geopolitical ukraine russia iran israel palestine gaza nato election
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

# Trasformo ogni elenco di parole in un insieme di parole
DIZ = {t: set(w.split()) for t, w in DIZ.items()}

SOGLIA, MARGINE, MIN_PAROLE = 0.010, 1.5, 30 # Le regole


def punteggia(testo):
    """Restituisce il tema della newsletter secondo il dizionario,
    oppure None se non si può decidere"""
    parole = re.findall(r"[a-z]+", testo.lower())
    if len(parole) < MIN_PAROLE:
        return None                                   

    score = {t: sum(w in v for w in parole) / len(parole) for t, v in DIZ.items()}

    # Prendo i due punteggi più alti
    primo, secondo = sorted(score.values(), reverse=True)[:2]
    if primo < SOGLIA:
        return None                                   # troppe poche parole del tema
    if secondo > 0 and primo / secondo < MARGINE:
        return None                                   # due temi quasi alla pari
    return max(score, key=score.get)                  # restituisco il tema con il punteggio più alto


# --- Applico il dizionario alle newsletter ancora deboli ---

# Leggo il tema di ogni newsletter
tema = dict(csv.reader(open(ELAB / "temi_finali.csv")))

cambi = Counter()   # qui conto quante newsletter passano da un tema a un altro
for riga in open(RACCOLTA / "testi_extra.jsonl"):
    d = json.loads(riga)
    u = d["url"]
    # Salto le newsletter che hanno già un tema buono 
    if tema.get(u) not in DEBOLI:
        continue
    # Unisco titolo, sottotitolo e corpo di tutti i post della newsletter in un unico testo
    testo = " ".join(f"{t.get('titolo') or ''} {t.get('sottotitolo') or ''} {t.get('corpo') or ''}"
                     for t in d.get("testi", []))
    nuovo = punteggia(testo)
    # Cambio il tema solo se il dizionario ha dato una risposta sicura
    if nuovo:
        cambi[f"{tema[u]} -> {nuovo}"] += 1
        tema[u] = nuovo

print(f"Riassegnati dal dizionario: {sum(cambi.values())} nodi")
# Stampo i 12 spostamenti più frequenti (da quale tema debole a quale tema nuovo)
for k, v in cambi.most_common(12):
    print(f"  {k:30} {v}")

# --- Aggiungo le newsletter non in inglese ---

# Le newsletter non in inglese con tema "non_english"
for u, l in carica_lingue().items():
    if l != "en":
        tema[u] = "non_english"

# Unisco le macro-categorie, prima quelle del dizionario, poi quelle di nomi_cluster.csv
# Alle newsletter non in inglese do la macro "unlabeled", cioè "senza categoria"
MACRO = {**MACRO_DIZ, **MACRO, "non_english": "unlabeled"}

# --- Salva la tabella finale una riga per newsletter con url, tema e macro-categoria ---

righe = [(u, t, MACRO[t]) for u, t in sorted(tema.items())]
with open(ELAB / "attributi_nodi.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["url", "tema", "macro"]); w.writerows(righe)

# --- Stampa un riepilogo ---

n_rete = len(lista_nodi()) # Numero totale di nodi nella rete 

# Numero newsletter per ogni tema e per ogni macro-categori
for titolo, col in [("TEMI FINI", 1), ("MACRO-CATEGORIE", 2)]:
    print(f"\n=== {titolo} (su {len(righe)} nodi con testo) ===")
    c = Counter(r[col] for r in righe)
    for t, n in c.most_common():
        print(f"  {t:18} {n:6} ({100*n/len(righe):.1f}%)")

# Conto le newsletter che hanno una macro-categoria vera 
utili = sum(r[2] != "unlabeled" for r in righe)
print(f"\nNodi della rete: {n_rete} | con testo: {len(righe)} | senza testo: {n_rete - len(righe)}")
print(f"Nodi con tema utilizzabile: {utili} ({100*utili/n_rete:.1f}% della rete)")