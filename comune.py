"""Funzioni condivise da più script.
Tutti i percorsi sono relativi alla cartella della repository."""

import csv
from pathlib import Path
import networkx as nx

# --- Percorsi delle cartelle ---

ROOT = Path(__file__).resolve().parent

DATA = ROOT / "data_collection" / "data"        # tutti i dati
RACCOLTA = DATA / "raccolta"                     # dati grezzi scaricati
ELAB = DATA / "elaborazione"                     # file prodotti dagli script
PLOT_NA = ROOT / "network_analysis" / "plots"    # grafici network analysis
PLOT_OP = ROOT / "open_problem" / "plots"        # grafici open problem

# Crea le cartelle se non esistono ancora
for d in (DATA, RACCOLTA, ELAB, PLOT_NA, PLOT_OP):
    d.mkdir(parents=True, exist_ok=True)


# --- Newsletter di partenza ---

# 15 newsletter da cui è partito il crawl, 3 per ognuna delle 5 aree tematiche
SEED_PER_AREA = {
    "arts_letters":   ["https://georgesaunders.substack.com", "https://footnotesandtangents.substack.com",
                       "https://pandorasykes.substack.com"],
    "politics":       ["https://greenwald.substack.com", "https://samf.substack.com",
                       "https://chrishedges.substack.com"],
    "technology":     ["https://natesnewsletter.substack.com", "https://newsletter.pragmaticengineer.com",
                       "https://damnang2.substack.com"],
    "finance":        ["https://michaeljburry.substack.com", "https://capitalwars.substack.com",
                       "https://charliepgarcia.substack.com"],
    "science_health": ["https://yourlocalepidemiologist.substack.com",
                       "https://theskepticalcardiologist.substack.com", "https://theunbiasedscipod.substack.com"],
}

# Gli stessi seed in un'unica lista
SEED = [u for lista in SEED_PER_AREA.values() for u in lista]


# --- Funzioni per caricare la rete ---

# Archi come coppie (sorgente, destinazione), senza self-loop
def archi_diretti():
    with open(DATA / "archi.csv", newline="") as f:
        return [(r["sorgente"], r["destinazione"]) for r in csv.DictReader(f)
                if r["sorgente"] != r["destinazione"]]


# Url di tutte le newsletter della rete
def lista_nodi():
    with open(DATA / "nodi.csv", newline="") as f:
        return [r["url"] for r in csv.DictReader(f)]


# Rete non diretta e non pesata, con tutti i nodi (anche quelli isolati)
def carica_grafo():
    G = nx.Graph()
    G.add_nodes_from(lista_nodi())
    G.add_edges_from(archi_diretti())
    return G


# Rete diretta, solo con i nodi che hanno almeno un arco
def carica_grafo_diretto():
    D = nx.DiGraph()
    D.add_edges_from(archi_diretti())
    return D


# --- Funzioni per caricare i risultati degli altri script ---

# Da attributi_nodi.csv: {url: tema} e {url: macro-categoria}
def carica_attributi():
    tema, macro = {}, {}
    with open(ELAB / "attributi_nodi.csv", newline="") as f:
        r = csv.reader(f); next(r)
        for u, t, m in r:
            tema[u] = t; macro[u] = m
    return tema, macro


# Da comunita.csv: {url: numero della comunità}
def carica_comunita():
    with open(ELAB / "comunita.csv", newline="") as f:
        r = csv.reader(f); next(r)
        return {u: int(c) for u, c in r}


# Accorcia un url per usarlo come etichetta ("https://greenwald.substack.com" -> "greenwald")
def corto(url):
    return url.replace("https://", "").replace(".substack.com", "")


# --- Testo e TF-IDF ---

# Parole non informative da ignorare, oltre alle stop word inglesi
PAROLE_VUOTE_EXTRA = """january february march april may june july august september october
 november december jan feb mar apr jun jul aug sep sept oct nov dec monday tuesday wednesday
 thursday friday saturday sunday week weekly daily monthly edition issue vol volume part episode
 ep newsletter substack update updates new don ve isn ll doesn didn""".split()


# TF-IDF usato per il clustering:
# - al massimo 20000 parole
# - scarta le parole presenti in meno di 5 newsletter o in più del 40%
# - sublinear_tf: le ripetizioni pesano in modo logaritmico
# - una parola ha almeno 2 lettere e nessun numero
def vettorizzatore():
    from sklearn.feature_extraction.text import TfidfVectorizer, ENGLISH_STOP_WORDS
    return TfidfVectorizer(max_features=20000, min_df=5, max_df=0.4, sublinear_tf=True,
                           stop_words=list(ENGLISH_STOP_WORDS | set(PAROLE_VUOTE_EXTRA)),
                           token_pattern=r"(?u)\b[a-zA-Z][a-zA-Z]+\b")


# {url: titolo + sottotitolo degli ultimi post}, solo se il testo ha almeno min_caratteri caratteri
def carica_titoli(min_caratteri=20):
    import json
    testi = {}
    for riga in open(RACCOLTA / "testi.jsonl"):
        d = json.loads(riga)
        t = " ".join(f"{x.get('titolo') or ''} {x.get('sottotitolo') or ''}" for x in d.get("testi", []))
        if len(t.strip()) >= min_caratteri:
            testi[d["url"]] = t
    return testi


# Da lingua_nodi.csv: {url: lingua}
def carica_lingue():
    with open(ELAB / "lingua_nodi.csv", newline="") as f:
        return dict(csv.reader(f))


# Da nomi_cluster.csv (compilato a mano): {cluster: (tema, macro, debole)}
# "debole" è True se la colonna contiene si, sì, s, 1 o yes (maiuscole e spazi ignorati)
def carica_nomi_cluster():
    with open(ELAB / "nomi_cluster.csv", newline="") as f:
        r = csv.DictReader(f)
        return {int(x["cluster"]): (x["tema"].strip(), x["macro"].strip(),
                                    x["debole"].strip().lower() in ("si", "sì", "s", "1", "yes"))
                for x in r}