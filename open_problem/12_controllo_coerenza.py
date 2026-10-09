"""CONTROLLO FINALE - verifica che tutti i file del dataset siano coerenti tra loro.
Da lanciare dopo tutti gli altri script. Stampa OK / ERRORE per ogni controllo."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import csv, json
import networkx as nx
import pandas as pd
from comune import DATA, RACCOLTA, ELAB, SEED

errori = 0


def check(cond, msg):
    global errori
    print(f"  {'OK    ' if cond else 'ERRORE'} {msg}")
    errori += not cond


nodi = pd.read_csv(DATA / "nodi.csv"); archi = pd.read_csv(DATA / "archi.csv")
N = set(nodi.url)
stato = json.load(open(RACCOLTA / "stato_crawl.json"))
grezze = pd.read_csv(RACCOLTA / "raccomandazioni_grezze.csv", names=["s", "t"]).drop_duplicates()

print("=== NODI E ARCHI (dataset finale) ===")
check(nodi.url.is_unique, f"nodi.csv: {len(nodi)} nodi, nessun duplicato")
check(N == set(stato["espansi"]) - set(stato.get("falliti", [])),
      "i nodi sono esattamente le newsletter espanse con successo dal crawl")
check(not set(stato.get("falliti", [])), f"nessun nodo fallito rimasto ({len(stato.get('falliti', []))})")
check(set(SEED) <= N, "tutti i 15 seed sono nella rete")
check(not archi.duplicated(["sorgente", "destinazione"]).any(), f"archi.csv: {len(archi)} archi, nessun duplicato")
check((archi.sorgente != archi.destinazione).all(), "nessun self-loop")
check(set(archi.sorgente) <= N and set(archi.destinazione) <= N, "ogni arco collega due nodi della rete")
indotto = grezze[grezze.s.isin(N) & grezze.t.isin(N) & (grezze.s != grezze.t)]
check(len(indotto) == len(archi), "archi.csv = sottografo indotto delle raccomandazioni grezze")
coppie = set(zip(archi.sorgente, archi.destinazione))
check(all(r == ((t, s) in coppie) for s, t, r in zip(archi.sorgente, archi.destinazione, archi.reciproca)),
      f"colonna 'reciproca' corretta (reciprocita' {archi.reciproca.mean():.3f})")
check((nodi.set_index("url").out_degree == archi.sorgente.value_counts().reindex(nodi.url, fill_value=0)).all(),
      "out_degree coerente con archi.csv")
check(archi.sorgente.value_counts().max() <= 50, "out-degree massimo <= 50 (tetto della piattaforma)")

print("\n=== ATTRIBUTI ===")
testi = {json.loads(r)["url"] for r in open(RACCOLTA / "testi.jsonl")}
check(N <= testi, f"testi.jsonl copre tutti i nodi ({len(testi)} righe)")
for f in ["lingua_nodi.csv", "cluster_nodi.csv", "temi_finali.csv"]:
    urls = {r[0] for r in csv.reader(open(ELAB / f))}
    check(urls <= N, f"{f}: {len(urls)} nodi, tutti nella rete")
attr = pd.read_csv(ELAB / "attributi_nodi.csv")
check(set(attr.url) <= N, f"attributi_nodi.csv: {len(attr)} nodi, tutti nella rete")
com = pd.read_csv(ELAB / "comunita.csv")
check(set(com.url) == N, f"comunita.csv copre tutti i nodi ({com.comunita.nunique()} comunita')")
for col in ["lingua", "tema", "macro_tema", "comunita", "comunita_etichetta"]:
    check(col in nodi and nodi[col].notna().all(), f"nodi.csv: colonna '{col}' presente e completa")
if "tema" in nodi:
    t = dict(zip(attr.url, attr.tema))
    check(all(t.get(u, "senza_testo") == v for u, v in zip(nodi.url, nodi.tema)), "nodi.csv: temi = attributi_nodi.csv")

print("\n=== GRAFO PER GEPHI ===")
G = nx.read_gexf(DATA / "grafo_finale.gexf")
U = nx.Graph(); U.add_edges_from(zip(archi.sorgente, archi.destinazione))
check(G.number_of_nodes() == len(nodi) and G.number_of_edges() == U.number_of_edges(),
      f"grafo_finale.gexf: {G.number_of_nodes()} nodi, {G.number_of_edges()} archi non diretti")

print(f"\n{'TUTTO COERENTE' if errori == 0 else f'{errori} CONTROLLI FALLITI'}")
