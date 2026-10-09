"""Percorsi e funzioni condivise da tutti gli script del progetto.
Tutti i percorsi sono relativi alla cartella della repository."""
import csv
from pathlib import Path
import networkx as nx

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data_collection" / "data"      # dataset finale: nodi.csv, archi.csv, grafo_finale.gexf
RACCOLTA = DATA / "raccolta"                   # dati grezzi della raccolta (crawl e testi)
ELAB = DATA / "elaborazione"                   # file intermedi della pipeline (temi, comunita')
PLOT_NA = ROOT / "network_analysis" / "plots"  # figure e tabelle di risultati della Parte 2
PLOT_OP = ROOT / "open_problem" / "plots"      # figure e tabelle di risultati della Parte 4
for d in (DATA, RACCOLTA, ELAB, PLOT_NA, PLOT_OP):
    d.mkdir(parents=True, exist_ok=True)


# le 15 newsletter di partenza del crawl, 3 per area (URL gia' normalizzati)
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
SEED = [u for lista in SEED_PER_AREA.values() for u in lista]


def archi_diretti():
    """Lista degli archi diretti (chi raccomanda, chi e' raccomandato), senza self-loop."""
    with open(DATA / "archi.csv", newline="") as f:
        return [(r["sorgente"], r["destinazione"]) for r in csv.DictReader(f)
                if r["sorgente"] != r["destinazione"]]


def lista_nodi():
    """Tutti i nodi della rete (anche quelli senza archi uscenti)."""
    with open(DATA / "nodi.csv", newline="") as f:
        return [r["url"] for r in csv.DictReader(f)]


def carica_grafo():
    """Rete non diretta, non pesata, semplice (come richiesto dalla Parte 2)."""
    G = nx.Graph()
    G.add_nodes_from(lista_nodi())
    G.add_edges_from(archi_diretti())
    return G


def carica_grafo_diretto():
    D = nx.DiGraph()
    D.add_edges_from(archi_diretti())
    return D


def carica_attributi():
    """url -> (tema fine, macro-categoria). Solo i nodi con testo sufficiente."""
    tema, macro = {}, {}
    with open(ELAB / "attributi_nodi.csv", newline="") as f:
        r = csv.reader(f); next(r)
        for u, t, m in r:
            tema[u] = t; macro[u] = m
    return tema, macro


def carica_comunita():
    with open(ELAB / "comunita.csv", newline="") as f:
        r = csv.reader(f); next(r)
        return {u: int(c) for u, c in r}


def corto(url):
    return url.replace("https://", "").replace(".substack.com", "")


# ---------- testo: corpus e TF-IDF condivisi dagli script 00, 01, 02 di open_problem ----------
PAROLE_VUOTE_EXTRA = """january february march april may june july august september october
 november december jan feb mar apr jun jul aug sep sept oct nov dec monday tuesday wednesday
 thursday friday saturday sunday week weekly daily monthly edition issue vol volume part episode
 ep newsletter substack update updates new don ve isn ll doesn didn""".split()


def vettorizzatore():
    """TF-IDF usato per il clustering tematico. Rispetto alla prima versione:
    - i token sono solo alfabetici (niente numeri/date: eliminava il finto tema 'date_only');
    - mesi, giorni e parole di servizio ('weekly', 'issue', 'update'...) sono parole vuote."""
    from sklearn.feature_extraction.text import TfidfVectorizer, ENGLISH_STOP_WORDS
    return TfidfVectorizer(max_features=20000, min_df=5, max_df=0.4, sublinear_tf=True,
                           stop_words=list(ENGLISH_STOP_WORDS | set(PAROLE_VUOTE_EXTRA)),
                           token_pattern=r"(?u)\b[a-zA-Z][a-zA-Z]+\b")


def carica_titoli(min_caratteri=20):
    """url -> testo (titolo+sottotitolo degli ultimi post), solo se c'e' abbastanza testo."""
    import json
    testi = {}
    for riga in open(RACCOLTA / "testi.jsonl"):
        d = json.loads(riga)
        t = " ".join(f"{x.get('titolo') or ''} {x.get('sottotitolo') or ''}" for x in d.get("testi", []))
        if len(t.strip()) >= min_caratteri:
            testi[d["url"]] = t
    return testi


def carica_lingue():
    with open(ELAB / "lingua_nodi.csv", newline="") as f:
        return dict(csv.reader(f))


def carica_nomi_cluster():
    """cluster -> (tema, macro, debole). File compilato a mano: data_collection/data/elaborazione/nomi_cluster.csv"""
    with open(ELAB / "nomi_cluster.csv", newline="") as f:
        r = csv.DictReader(f)
        return {int(x["cluster"]): (x["tema"].strip(), x["macro"].strip(),
                                    x["debole"].strip().lower() in ("si", "sì", "s", "1", "yes"))
                for x in r}
