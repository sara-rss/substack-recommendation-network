"""Percorsi e funzioni condivise da tutti gli script del progetto.
Tutti i percorsi sono relativi alla cartella della repository."""
import csv
from pathlib import Path
import networkx as nx

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data_collection" / "data"      # TUTTI i dati: raccolti, rete finale e attributi dei nodi
PLOT_NA = ROOT / "network_analysis" / "plots"  # figure e tabelle di risultati della Parte 2
PLOT_OP = ROOT / "open_problem" / "plots"      # figure e tabelle di risultati della Parte 4
for d in (DATA, PLOT_NA, PLOT_OP):
    d.mkdir(parents=True, exist_ok=True)


def archi_diretti():
    """Lista degli archi diretti (chi raccomanda, chi e' raccomandato), senza self-loop."""
    with open(DATA / "rete_finale.csv", newline="") as f:
        return [(s, t) for s, t in csv.reader(f) if s != t]


def carica_grafo():
    """Rete non diretta, non pesata, semplice (come richiesto dalla Parte 2)."""
    G = nx.Graph()
    with open(DATA / "nodi_finali.csv") as f:
        G.add_nodes_from(riga.strip() for riga in f if riga.strip())
    G.add_edges_from(archi_diretti())
    return G


def carica_grafo_diretto():
    D = nx.DiGraph()
    D.add_edges_from(archi_diretti())
    return D


def carica_attributi():
    """url -> (tema fine, macro-categoria). Solo i nodi con testo sufficiente."""
    tema, macro = {}, {}
    with open(DATA / "attributi_nodi.csv", newline="") as f:
        r = csv.reader(f); next(r)
        for u, t, m in r:
            tema[u] = t; macro[u] = m
    return tema, macro


def carica_comunita():
    with open(DATA / "comunita.csv", newline="") as f:
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
    for riga in open(DATA / "testi.jsonl"):
        d = json.loads(riga)
        t = " ".join(f"{x.get('titolo') or ''} {x.get('sottotitolo') or ''}" for x in d.get("testi", []))
        if len(t.strip()) >= min_caratteri:
            testi[d["url"]] = t
    return testi


def carica_lingue():
    with open(DATA / "lingua_nodi.csv", newline="") as f:
        return dict(csv.reader(f))


def carica_nomi_cluster():
    """cluster -> (tema, macro, debole). File compilato a mano: data_collection/data/nomi_cluster.csv"""
    with open(DATA / "nomi_cluster.csv", newline="") as f:
        r = csv.DictReader(f)
        return {int(x["cluster"]): (x["tema"].strip(), x["macro"].strip(),
                                    x["debole"].strip().lower() in ("si", "sì", "s", "1", "yes"))
                for x in r}
