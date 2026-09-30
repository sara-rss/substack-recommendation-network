# Part 2 — Network analysis

Tutte le misure sono calcolate sulla versione **non diretta, non pesata, semplice** della rete
(la versione diretta è usata solo per reciprocità e PageRank diretto). Figure e risultati (json) in `plots/`.

| Script | Analisi |
|---|---|
| `p2_1_gradi.py` | distribuzione del grado, hub, reciprocità, assortatività di grado, **test sulla coda** (power law vs lognormale vs power law troncata, pacchetto `powerlaw`) |
| `p2_2_componenti.py` | componenti connesse, densità |
| `p2_3_cammini.py` | cammino medio e diametro **esatti**, distribuzione delle distanze |
| `p2_4_clustering.py` | clustering medio, transitività, triangoli, clustering per fascia di grado |
| `p2_5_centralita.py` | degree, PageRank (non diretto e diretto), betweenness **esatta**, correlazioni, nodi-ponte |
| `p2_6_confronto.py` | confronto con ER e BA (10 realizzazioni per modello, media ± dev. std.; BA con m=5 e m=6; ~20 minuti) |
