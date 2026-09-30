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
| `01_crawl.py` | crawl con checkpoint e ripresa automatica → `data/archi.csv`, `data/stato.json` |
| `02_riprova_falliti.py` | riprova i nodi la cui richiesta era fallita; chi fallisce ancora viene escluso |
| `03_costruisci_rete.py` | sottografo indotto → `data/rete_finale.csv`, `data/nodi_finali.csv` |
| `04_scarica_testi.py` | titolo+sottotitolo degli ultimi 10 post di ogni nodo → `data/testi.jsonl` |
| `05_scarica_corpo.py` | inizio del corpo dei post per i nodi tematicamente "deboli" → `data/testi_extra.jsonl` |
| `06_verifica_testi.py` | controllo di copertura dei testi |
| `esplorazione/` | prove iniziali dell'API (mostrano, tra l'altro, che la categoria ufficiale non è esposta) |

**Limiti dichiarati**
- Lo snowball raggiunge solo nodi collegati ai seed: l'unica componente connessa è in parte un effetto del metodo; i nodi molto raccomandati sono sovra-rappresentati.
- Substack mostra al massimo **50 raccomandazioni** per newsletter: l'out-degree è troncato a 50.
- Gli archi verso nodi non espansi sono esclusi: il grado dei nodi scoperti per ultimi è sottostimato.
- Gli attributi tematici sono ricavati dal testo (vedi `open_problem/`), perché la categoria ufficiale non è accessibile.

**Dati** (`data/`, compressi in `data.zip`)
| File | Contenuto |
|---|---|
| `archi.csv` | tutte le raccomandazioni raccolte dal crawl (dirette, anche verso nodi non espansi) |
| `stato.json` | stato finale del crawl: nodi espansi, scoperti, in coda, falliti |
| `rete_finale.csv`, `nodi_finali.csv` | **la rete analizzata**: archi diretti tra nodi espansi e lista dei nodi |
| `testi.jsonl`, `testi_extra.jsonl` | titoli/sottotitoli degli ultimi post; corpo dei post per i nodi tematicamente deboli |
| `stato_testi.json`, `stato_extra.json` | checkpoint dei due download dei testi |
| `lingua_nodi.csv` | lingua di ogni newsletter |
| `cluster_nodi.csv`, `nomi_cluster.csv` | cluster tematico di ogni nodo (congelato) e nome/macro-categoria di ogni cluster (assegnati a mano) |
| `temi_finali.csv`, `attributi_nodi.csv` | tema dopo il recupero col corpo; **attributi finali** (tema fine e macro-categoria) |
| `comunita.csv` | comunità di riferimento (Louvain) |
| `grafo_finale.gexf` | rete per Gephi con lingua, tema, macro-categoria e comunità |
