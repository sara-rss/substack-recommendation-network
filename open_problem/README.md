
# Part 4: Open Question — Topic Attributes and Community Structure

## The Core Question
> Do the communities formed by recommendations simply mirror the topics of the newsletters, or do they, in some domains, separate newsletters that write about the same subject from different perspectives?

## Data and Outputs Overview
- **Visualizations**: All result figures and tables are generated in the `plots/` directory.
- **Node Attributes**: Files containing one value per node (language, topic, community) are stored in `data_collection/data/elaborazione/`.
- **Master Dataset**: All attributes are ultimately merged into the master file: `data_collection/data/nodi.csv`.

---

## Phase A: Topic Inference Pipeline (Scripts 00–04)

Because Substack does not expose the official category of third-party publications, newsletter topics must be inferred directly from the text of their posts. This pipeline isolates English-language newsletters and applies a multi-stage classification process.

- **`00_scegli_k.py`** (Exploratory): Evaluates the elbow method and silhouette scores for various values of *k*. While neither metric indicates a sharp optimum, **k = 16** is selected as the smallest value that successfully separates the five seed areas into distinct clusters.
- **`01_clustering_temi.py`** (Primary Clustering): 
  1. Detects the language of each newsletter. The 387 non-English newsletters (2.5% of the network) are excluded from clustering and tagged with language as a separate attribute.
  2. Runs TF–IDF + *k*-means on post titles and subtitles, filtering out numbers, dates, and stop words. 
  3. *Note*: This script is designed to be run **only once**. Because *k*-means results can vary across scikit-learn versions, the output is frozen in `data/elaborazione/cluster_nodi.csv`. Macro-topics and "weak" flags are manually assigned in `data/elaborazione/nomi_cluster.csv` after inspecting characteristic terms (`plots/cluster_parole.csv`).
- **`02_riclassifica_corpo.py`** (Body Text Refinement): Newsletters initially placed in "weak" clusters are reassigned to the nearest existing centroid using the full post bodies. This step is deterministic and does not re-run *k*-means.
- **`03_riclassifica_dizionario.py`** (Dictionary Recovery): A final recovery step for ambiguous cases using a custom dictionary of unambiguous keywords and conservative thresholds. Outputs to `data/elaborazione/attributi_nodi.csv`.
- **`04_valida_seed.py`** (Validation): Performs a consistency check on the 15 seed newsletters, whose areas are known *a priori*. Result: 12 of 15 are assigned correctly. *(Note: This is not a fully independent validation, as the seed areas also guided the initial choice of k).*

---

## Phase B: Community Detection and Validation (Scripts 05–10b)

This phase maps the network's community structure and rigorously tests its relationship with the inferred text-based topics.

- **`05_comunita.py`** (Community Detection): Runs the Louvain algorithm 30 times. The reference partition is selected as the one most similar on average to all other runs. Like the clustering step, this is run **once** and frozen in `data/elaborazione/comunita.csv` to ensure reproducibility (subsequent runs yield equivalent, but not identical, partitions).
- **`06_stabilita_comunita.py`** (Stability Analysis): Evaluates the robustness of the partition with respect to random seeds and algorithms (30 Louvain runs + 30 Leiden runs). Measures the cohesion of each community and identifies which communities most frequently merge.
- **`07_comunita_vs_temi.py`** (Topic Assortativity): Calculates Normalized Mutual Information (NMI), topical assorativity, homogeneity, and completeness between communities and topics. Crucially, this comparison is benchmarked against a **label-permutation null model** to ensure statistical significance, using only text-based labels.
- **`08_profilo_comunita.py`** (Community Profiling): Generates a detailed profile for each major community, including size, dominant topic, fine-grained topics, and central newsletters. Labels are anchored to well-known newsletters for interpretability.
- **`09_label_mancanti.py`** (Missing Labels Analysis): Investigates nodes without topic labels *without* reclassifying them. Analyzes why labels are missing, whether they concentrate in peripheral nodes or specific communities, and assesses how reliable a community's dominant topic is as a proxy for its unlabeled members. Generates the missing-labels figure for the main report.
- **`10_grafo_gexf.py`** (Final Export): Compiles the final dataset. Completes `data/nodi.csv` with all attributes (including English community names) and exports `data/grafo_finale.gexf` for Gephi, pre-configured with colors, sizes, and ForceAtlas2 positions.
- **`10b_figura_rete.py`** (Network Visualization): Generates the final network figure for the report (`plots/rete_comunita.png`). The ForceAtlas2 layout is computed once in Gephi and frozen in `data/posizioni_fa2.csv`; visual styling (colors and names) is applied via `stile_rete.py` in the root directory.

