"""Esporta la rete per Gephi con tema, macro-categoria, comunita' ed etichetta della comunita'."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import csv
import networkx as nx
from comune import DATA, carica_grafo, carica_attributi, carica_comunita, carica_lingue, PLOT_OP

G = carica_grafo(); tema, macro = carica_attributi(); com = carica_comunita()
et = {int(r[0]): r[3] for r in list(csv.reader(open(PLOT_OP / "comunita_etichette.csv")))[1:]}
nx.set_node_attributes(G, {n: tema.get(n, "senza_testo") for n in G}, "tema")
nx.set_node_attributes(G, {n: macro.get(n, "unlabeled") for n in G}, "macro")
lingua = carica_lingue()
nx.set_node_attributes(G, {n: lingua.get(n, "?") for n in G}, "lingua")
nx.set_node_attributes(G, {n: com[n] for n in G}, "comunita")
nx.set_node_attributes(G, {n: et.get(com[n], "marginale") for n in G}, "comunita_etichetta")
nx.write_gexf(G, DATA / "grafo_finale.gexf")
print(f"Salvato grafo_finale.gexf ({G.number_of_nodes()} nodi, {G.number_of_edges()} archi)")
