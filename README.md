# Substack recommendation network — SNA Final Project 2026

**Sara Rossi** (matricola 637107) — progetto individuale (Parte 3 omessa come da regolamento).

Rete delle **raccomandazioni tra newsletter Substack**: i nodi sono newsletter, un arco A→B significa
"A raccomanda B ai propri lettori". Domanda di ricerca (Parte 4): *le raccomandazioni dividono le
newsletter per argomento o secondo confini più fini (per esempio ideologici) che dal testo non si vedono?*

## Struttura
| Percorso | Contenuto |
|---|---|
| `data_collection/` | crawling, costruzione della rete, scaricamento dei testi |
| `data_collection/data/` | **tutti i dati** (compressi in `data_collection/data.zip`): archi raccolti, rete finale, testi, attributi dei nodi, comunità, grafo per Gephi |
| `network_analysis/` | Parte 2: gradi, componenti, cammini, clustering, centralità, confronto ER/BA |
| `open_problem/` | attributi tematici dei nodi e Parte 4 |
| `network_analysis/plots/`, `open_problem/plots/` | figure e tabelle di risultati |
| `report/` | report finale |
| `comune.py` | percorsi e funzioni di caricamento condivise da tutti gli script |

## Come riprodurre i risultati
```
pip install -r requirements.txt
unzip data_collection/data.zip -d data_collection/
```
Gli script si lanciano da dentro la loro cartella, nell'ordine del numero nel nome. I passi di
scraping (⏳) richiedono ore e i loro risultati sono già nei dati; il clustering tematico (✱) è
eseguito una sola volta e il suo risultato è congelato in `data/cluster_nodi.csv`. Per riprodurre
le analisi basta quindi partire dal punto 4.

1. `data_collection/`: `01_crawl.py` ⏳ → `02_riprova_falliti.py` → `03_costruisci_rete.py` → `04_scarica_testi.py` ⏳ → `06_verifica_testi.py`
2. `open_problem/01_clustering_temi.py` ✱ (poi i nomi dei cluster si assegnano a mano in `data/nomi_cluster.csv`); `00_scegli_k.py` documenta la scelta di k
3. `data_collection/05_scarica_corpo.py` ⏳
4. `open_problem/`: `02_riclassifica_corpo.py` → `03_riclassifica_dizionario.py` → `04_valida_seed.py`
5. `network_analysis/`: `p2_1_gradi.py` … `p2_6_confronto.py` (indipendenti tra loro)
6. `open_problem/`: `05_comunita.py` → `06_stabilita_comunita.py` → `07_comunita_vs_temi.py` → `08_profilo_comunita.py` → `09_label_mancanti.py` → `10_grafo_gexf.py` → `11_esempi_label_mancanti.py`
