

# Part 1: Data Collection 

## Data Source and Network Definition

**Source:** Substack, accessed via the unofficial `substack-api` library (for recommendations) and the public `/api/v1/archive` endpoint (for posts). All requests were rate-limited to one per second and sent with an identifying User-Agent. Data collection was completed in August 2026.

**Network Definition:**
- **Nodes:** Newsletters.
- **Edges:** Recommendations (Directed: A recommends B). 


## The Data Pipeline 

| Script | Function and Output |
| :--- | :--- |
| `01_crawl.py` | Executes the BFS crawl with checkpoints and automatic resume capabilities. Outputs: `data/raccolta/raccomandazioni_grezze.csv`, `data/raccolta/stato_crawl.json`. |
| `02_riprova_falliti.py` | Retries requests for newsletters that failed during the initial crawl (59 failures, all successfully recovered). |
| `03_costruisci_rete.py` | Builds the final induced subgraph from the raw crawl data. Outputs: `data/archi.csv`, `data/nodi.csv`. |
| `04_scarica_testi.py` | Downloads the titles and subtitles of the 10 most recent posts for each node. Outputs: `data/raccolta/testi.jsonl`. |
| `05_scarica_corpo.py` | Downloads the beginning of post bodies specifically for newsletters in weak topic clusters. Outputs: `data/raccolta/testi_extra.jsonl` *(Requires `nomi_cluster.csv` from the `open_problem/` pipeline).* |
| `06_verifica_testi.py` | Validates and checks overall text coverage across the dataset. |
| `esplorazione/` | Directory containing preliminary API testing scripts used before the main crawl: `prova_substack.py` (seed recommendations), `prova_api.py` (posts endpoint), and `prova_metadati.py` (metadata availability, confirming official categories are not exposed). |


## Data Dictionary and File Structure

All data is stored in the `data/` directory and compressed in `data.zip`.

### Final Dataset 

| File | Contents |
| :--- | :--- |
| `nodi.csv` | One row per newsletter. Columns: `url`, `seed` (1 = seed newsletter), `lingua`, `tema`, `macro_tema`, `comunita`, `comunita_etichetta`, `comunita_label` (English community name), `grado`, `in_degree`, `out_degree`. |
| `archi.csv` | One row per recommendation. Columns: `sorgente` (recommends) `destinazione`; `reciproca` = 1 if the destination also recommends the source (occurs in 41% of recommendations). |
| `grafo_finale.gexf` | The undirected network formatted for Gephi, including all attributes, colors, sizes, and pre-computed positions. |
| `posizioni_fa2.csv` | Node coordinates computed once using ForceAtlas2 in Gephi (provides the frozen layout for the final network visualization). |

### `raccolta/` — Raw Data (As produced by download scripts)

| File | Contents |
| :--- | :--- |
| `raccomandazioni_grezze.csv` | All raw recommendations collected during the crawl, including edges pointing to non-expanded newsletters. |
| `stato_crawl.json` | Final state of the crawler: tracks expanded, discovered, queued, and failed newsletters. |
| `testi.jsonl`, `testi_extra.jsonl` | Raw text data: titles/subtitles of the 10 most recent posts, and post body excerpts for weak-cluster newsletters. |
| `stato_testi.json`, `stato_extra.json` | Checkpoint files tracking the progress of the two text download scripts. |

### `elaborazione/` — Intermediate Pipeline Files

*Note: These files are generated during the topic inference pipeline and are ultimately merged into the final `nodi.csv`.*

| File | Contents |
| :--- | :--- |
| `lingua_nodi.csv` | Detected language for each newsletter. |
| `cluster_nodi.csv`, `nomi_cluster.csv` | Initial topic cluster assignments (frozen). Includes the manually assigned name, macro-topic, and "weak" flag for each cluster based on characteristic terms. |
| `temi_finali.csv`, `attributi_nodi.csv` | Refined topic assignments after the post-body recovery step. Contains the final topic and macro-topic labels. |
| `comunita.csv` | The reference community partition (Louvain algorithm, frozen). |

