# Part 1 — Data collection

**Fonte:** Substack, tramite la libreria non ufficiale `substack-api` (raccomandazioni) e
l'endpoint pubblico `/api/v1/archive` (post). Pausa di 1 s tra le richieste, User-Agent identificativo.

**Nodi** = newsletter. **Archi** = raccomandazioni (dirette: A raccomanda B). È un legame *osservato*
e deliberato (chi raccomanda cede attenzione dei propri lettori), non una similarità calcolata.

**Strategia:** snowball sampling in ampiezza (BFS) da 15 seed scelti a mano, 3 per ciascuna di 5 aree
(letteratura, politica, tecnologia, finanza, scienza). Il crawl è stato fermato manualmente superata
la soglia richiesta. La **rete finale è il sottografo indotto sui nodi espansi con successo**: per ogni
nodo conosciamo tutte le raccomandazioni in uscita. I nodi solo "scoperti" (in coda) sono esclusi.

| Script | Cosa fa |
|---|---|
| `01_crawl.py` | crawl con checkpoint e ripresa automatica → `data/raccolta/raccomandazioni_grezze.csv`, `data/raccolta/stato_crawl.json` |
| `02_riprova_falliti.py` | riprova i nodi la cui richiesta era fallita; chi fallisce ancora viene escluso |
| `03_costruisci_rete.py` | sottografo indotto → `data/archi.csv`, `data/nodi.csv` |
| `04_scarica_testi.py` | titolo+sottotitolo degli ultimi 10 post di ogni nodo → `data/raccolta/testi.jsonl` |
| `05_scarica_corpo.py` | inizio del corpo dei post per i nodi tematicamente "deboli" → `data/raccolta/testi_extra.jsonl` |
| `06_verifica_testi.py` | controllo di copertura dei testi |
| `esplorazione/` | prove iniziali dell'API (mostrano, tra l'altro, che la categoria ufficiale non è esposta) |

**Limiti dichiarati**
- Lo snowball raggiunge solo nodi collegati ai seed: l'unica componente connessa è in parte un effetto del metodo; i nodi molto raccomandati sono sovra-rappresentati.
- Substack mostra al massimo **50 raccomandazioni** per newsletter: l'out-degree è troncato a 50.
- Gli archi verso nodi non espansi sono esclusi: il grado dei nodi scoperti per ultimi è sottostimato.
- Gli attributi tematici sono ricavati dal testo (vedi `open_problem/`), perché la categoria ufficiale non è accessibile.

**Dati** (`data/`, compressi in `data.zip`)

*Dataset finale* — quello da usare per qualsiasi analisi:
| File | Contenuto |
|---|---|
| `nodi.csv` | una riga per newsletter: `url`, `seed` (1 = newsletter di partenza), `lingua`, `tema`, `macro_tema`, `comunita`, `comunita_etichetta`, `grado`, `in_degree`, `out_degree` |
| `archi.csv` | una riga per raccomandazione: `sorgente` raccomanda `destinazione`; `reciproca` = 1 se anche `destinazione` raccomanda `sorgente` |
| `grafo_finale.gexf` | la rete non diretta con gli stessi attributi, per Gephi |

*`raccolta/`* — dati grezzi, come prodotti dagli script di scraping:
| File | Contenuto |
|---|---|
| `raccomandazioni_grezze.csv` | tutte le raccomandazioni raccolte dal crawl, anche verso newsletter non espanse |
| `stato_crawl.json` | stato finale del crawl: nodi espansi, scoperti, in coda, falliti |
| `testi.jsonl`, `testi_extra.jsonl` | titoli/sottotitoli degli ultimi 10 post; corpo dei post per i nodi tematicamente deboli |
| `stato_testi.json`, `stato_extra.json` | checkpoint dei due download dei testi |

*`elaborazione/`* — file intermedi della pipeline (i loro contenuti confluiscono in `nodi.csv`):
| File | Contenuto |
|---|---|
| `lingua_nodi.csv` | lingua di ogni newsletter |
| `cluster_nodi.csv`, `nomi_cluster.csv` | cluster tematico di ogni nodo (congelato) e nome/macro-categoria di ogni cluster (assegnati a mano) |
| `temi_finali.csv`, `attributi_nodi.csv` | tema dopo il recupero col corpo; tema finale e macro-categoria |
| `comunita.csv` | comunità di riferimento (Louvain) |
