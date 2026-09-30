# Part 4 — Open question (+ attributi tematici dei nodi)

**Domanda:** le raccomandazioni tra newsletter dividono la rete per argomento, o secondo confini più
fini (per esempio ideologici) che dal testo non si vedono?

Figure e tabelle di risultati sono in `plots/`; i file con un valore per nodo (attributi, comunità)
sono in `data_collection/data/`.

## A. Attributi tematici dei nodi (script 00–04)
Substack non espone la categoria delle pubblicazioni, quindi il tema è ricavato dai testi dei post.
- `00_scegli_k.py` — esplorativo: gomito e silhouette per diversi k. Non esiste un k "ottimale" netto; si è scelto **k=16**, il più piccolo per cui le 5 aree dei seed emergono come cluster distinti.
- `01_clustering_temi.py` — rileva la **lingua** di ogni newsletter (le non inglesi, ~3%, restano fuori dal clustering e la lingua è un attributo a parte), poi TF-IDF + KMeans su titolo+sottotitolo, ignorando numeri, date e parole di servizio. Eseguito **una sola volta**: KMeans non dà gli stessi cluster su versioni diverse di scikit-learn, quindi il risultato è congelato in `data/cluster_nodi.csv`. Nome, macro-categoria e flag "debole" di ogni cluster sono assegnati a mano in `data/nomi_cluster.csv`, guardando le parole caratteristiche (`plots/cluster_parole.csv`).
- `02_riclassifica_corpo.py` — i nodi dei cluster deboli sono riassegnati usando anche il corpo dei post (assegnazione deterministica al centroide più vicino, senza rifare KMeans).
- `03_riclassifica_dizionario.py` — ultimo recupero con un dizionario di parole non ambigue e soglie prudenziali → `data/attributi_nodi.csv`.
- `04_valida_seed.py` — validazione sui 15 seed di categoria nota.

## B. Comunità e temi (script 05–11)
- `05_comunita.py` — Louvain eseguito 30 volte; partizione di riferimento = la più simile in media alle altre.
- `06_stabilita_comunita.py` — stabilità rispetto a seed e algoritmo (Louvain + Leiden, 60 esecuzioni): coesione di ogni comunità e probabilità di fusione con le altre.
- `07_comunita_vs_temi.py` — assortatività tematica, NMI comunità-tema e **modello nullo** per permutazione. Usa solo le label ricavate dal testo.
- `08_profilo_comunita.py` — carta d'identità di tutte le comunità principali; etichette agganciate a newsletter-ancora.
- `09_label_mancanti.py` — analisi delle **label mancanti** (nessuna riclassificazione): perché mancano, se si concentrano nei nodi periferici o in alcune comunità, e quanto il tema dominante della comunità sarebbe un'indicazione affidabile per i nodi senza label.
- `10_grafo_gexf.py` — esportazione per Gephi.
- `11_esempi_label_mancanti.py` — illustrativo: esempi di newsletter senza label, con i titoli dei post e il tema dominante della loro comunità.
