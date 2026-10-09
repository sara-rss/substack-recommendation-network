"""Figura della rete per il report (larghezza testo a due colonne, 7.16 in, 600 dpi).
Legge data/nodi.csv (scritto da 10_grafo_gexf.py), data/posizioni_fa2.csv (layout congelato) e la rete
non diretta da comune.carica_grafo(); colori, nomi e dimensioni da stile_rete.py.
Produce in open_problem/plots/:
  rete_comunita.png       tutti i nodi
  rete_comunita_wide.png  inquadratura piu' bassa: taglia in verticale lo 0.12% dei nodi piu'
                          estremi (code 'Other (marginal)'), da segnalare in didascalia."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.lines import Line2D
from comune import DATA, PLOT_OP, carica_grafo
from stile_rete import COMUNITA, COLORE, FILE_POSIZIONI, OPACITA_ARCHI, dimensione_nodo

LARGHEZZA = 7.16          # pollici
K = LARGHEZZA / 13        # scala di spessori/marker rispetto alla versione di riferimento a 13 in

nodi = pd.read_csv(DATA / "nodi.csv").merge(pd.read_csv(DATA / FILE_POSIZIONI), on="url", how="left")
assert nodi[["x", "y"]].notna().all().all(), "nodi senza posizione"
G = carica_grafo()
idx = {u: i for i, u in enumerate(nodi.url)}
xy = nodi[["x", "y"]].to_numpy()
col = np.array([matplotlib.colors.to_rgb(COLORE[e]) for e in nodi.comunita_etichetta])
dim = np.array([dimensione_nodo(g, nodi.grado.max()) for g in nodi.grado])
s = np.array([idx[u] for u, _ in G.edges()]); t = np.array([idx[v] for _, v in G.edges()])
o = np.random.default_rng(0).permutation(len(s)); s, t = s[o], t[o]   # ordine misto, come Gephi

def disegna(out, crop=False):
    if crop:
        lo = np.array([xy[:, 0].min(), np.percentile(xy[:, 1], 0.12)])
        hi = np.array([xy[:, 0].max(), np.percentile(xy[:, 1], 99.88)])
    else:
        lo, hi = xy.min(0), xy.max(0)
    span = hi - lo; pad = 0.01 * span
    H = LARGHEZZA * (span[1] + 2 * pad[1]) / (span[0] + 2 * pad[0]); L = 0.75   # L = spazio legenda
    fig = plt.figure(figsize=(LARGHEZZA, H + L), facecolor="white")
    ax = fig.add_axes([0, L / (H + L), 1, H / (H + L)])
    ax.add_collection(LineCollection(np.stack([xy[s], xy[t]], 1),
                                     colors=np.c_[col[s], np.full(len(s), OPACITA_ARCHI)], linewidths=0.25 * K))
    ax.scatter(xy[:, 0], xy[:, 1], s=(dim * 0.55 * K) ** 2, c=col, linewidths=0, zorder=3)
    ax.set_xlim(lo[0] - pad[0], hi[0] + pad[0]); ax.set_ylim(lo[1] - pad[1], hi[1] + pad[1])
    ax.set_aspect("equal"); ax.axis("off")
    maniglie = [Line2D([0], [0], color=c, lw=2.5, solid_capstyle="butt") for _, _, c in COMUNITA]
    fig.legend(maniglie, [en for _, en, _ in COMUNITA], loc="upper center", bbox_to_anchor=(0.5, L / (H + L)),
               ncol=4, frameon=False, fontsize=8, handlelength=1.8, columnspacing=1.6,
               handletextpad=0.6, labelspacing=0.5)
    fig.savefig(out, dpi=600, facecolor="white", bbox_inches=None if crop else "tight", pad_inches=0.03)
    plt.close(fig)
    if crop:
        fuori = ((xy[:, 1] < lo[1]) | (xy[:, 1] > hi[1])).sum()
        print(f"{out.name}: {fuori} nodi fuori cornice")
    print("Salvata", out)

disegna(PLOT_OP / "rete_comunita.png")
disegna(PLOT_OP / "rete_comunita_wide.png", crop=True)
