"""PARTE 2.2 - Componenti connesse e densità."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from comune import carica_grafo, carica_grafo_diretto

import networkx as nx

G, D = carica_grafo(), carica_grafo_diretto()

# Componenti connesse della rete non diretta, dalla più grande alla più piccola
comp = sorted(nx.connected_components(G), key=len, reverse=True)
print(f"Componenti connesse: {len(comp)}")
print(f"Componente gigante: {len(comp[0])} nodi "
      f"({100*len(comp[0])/G.number_of_nodes():.2f}%)")
if len(comp) > 1:
    print("Altre componenti:", [len(c) for c in comp[1:11]])   # dimensioni delle 10 componenti successive

# Componente fortemente connessa più grande della rete diretta:
# nodi che possono raggiungersi a vicenda seguendo la direzione degli archi
scc = max(nx.strongly_connected_components(D), key=len)
print(f"\nRete diretta - componente fortemente connessa più grande: {len(scc)} nodi "
      f"({100*len(scc)/D.number_of_nodes():.1f}%)")

# Densità della rete non diretta: archi presenti / archi possibili
print(f"Densità: {nx.density(G):.6f}")