"""PARTE 2.1 - Distribuzione del grado: statistiche, hub, grafici, reciprocita',
assortativita' di grado e test statistico sulla forma della coda (pacchetto powerlaw)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from comune import carica_grafo, carica_grafo_diretto, PLOT_NA, corto

import json
import numpy as np, networkx as nx, powerlaw
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from collections import Counter

G, D = carica_grafo(), carica_grafo_diretto()
gradi = np.array([d for _, d in G.degree()])
print(f"Nodi: {G.number_of_nodes()}   Archi (non diretti): {G.number_of_edges()}")
print(f"Grado medio: {gradi.mean():.2f} | mediano: {np.median(gradi):.0f} | "
      f"min: {gradi.min()} | max: {gradi.max()} | dev.std: {gradi.std():.2f}")
print(f"Nodi con grado 1: {(gradi == 1).sum()} ({100*(gradi == 1).mean():.1f}%)")

print("\n--- top 10 hub ---")
for nodo, d in sorted(G.degree(), key=lambda x: -x[1])[:10]:
    print(f"  {d:4}  {corto(nodo)}")

# --- informazioni dalla rete DIRETTA (chi raccomanda chi) ---
outd = [d for _, d in D.out_degree()]; ind = [d for _, d in D.in_degree()]
rec = nx.reciprocity(D)
print(f"\nArchi diretti: {D.number_of_edges()}  ->  non diretti: {G.number_of_edges()}")
print(f"Reciprocita': {rec:.3f}  (quota di raccomandazioni ricambiate)")
print(f"Out-degree max: {max(outd)} (tetto di 50 raccomandazioni; "
      f"{sum(d == 50 for d in outd)} nodi al tetto) | In-degree max: {max(ind)}")
ass = nx.degree_assortativity_coefficient(G)
print(f"Assortativita' di grado: {ass:.3f}  (<0: gli hub si collegano a nodi piccoli)")

# --- la coda e' una legge di potenza? (metodo Clauset-Shalizi-Newman) ---
print("\n--- test sulla coda della distribuzione ---")
fit = powerlaw.Fit(gradi, discrete=True, verbose=False)
print(f"k_min = {fit.xmin:.0f} | alpha = {fit.alpha:.2f} | "
      f"nodi nella coda: {(gradi >= fit.xmin).sum()}")
confronti = {}
for alt in ["lognormal", "truncated_power_law", "exponential"]:
    R, p = fit.distribution_compare("power_law", alt, normalized_ratio=True)
    esito = "power law migliore" if R > 0 else f"{alt} migliore"
    print(f"  power law vs {alt:20} R = {R:+.2f}  p = {p:.2g}  -> {esito}"
          f"{'' if p < 0.05 else ' (non significativo)'}")
    confronti[alt] = {"R": R, "p": p}
json.dump({"kmin": fit.xmin, "alpha": fit.alpha, "confronti": confronti,
           "reciprocita": rec, "assortativita_grado": ass},
          open(PLOT_NA / "gradi.json", "w"), indent=1)

# --- grafici ---
plt.figure(figsize=(7, 5))
plt.hist(gradi, bins=60, color="steelblue", edgecolor="white")
plt.xlabel("Grado (k)"); plt.ylabel("Numero di nodi")
plt.title("Distribuzione del grado (scala lineare)")
plt.tight_layout(); plt.savefig(PLOT_NA / "grado_lineare.png", dpi=150); plt.close()

c = Counter(gradi); x = sorted(c); y = [c[k] / len(gradi) for k in x]
plt.figure(figsize=(7, 5))
plt.scatter(x, y, s=15, color="crimson")
plt.xscale("log"); plt.yscale("log")
plt.xlabel("Grado (k)"); plt.ylabel("P(k)")
plt.title("Distribuzione del grado (log-log)")
plt.tight_layout(); plt.savefig(PLOT_NA / "grado_loglog.png", dpi=150); plt.close()

# CCDF con i fit sovrapposti: e' il grafico giusto per giudicare la coda
plt.figure(figsize=(7, 5))
fit.plot_ccdf(color="crimson", linewidth=0, marker="o", markersize=3, label="dati (coda)")
fit.power_law.plot_ccdf(color="black", linestyle="--", label=f"power law (α={fit.alpha:.2f})")
fit.lognormal.plot_ccdf(color="seagreen", linestyle="-", label="lognormale")
fit.truncated_power_law.plot_ccdf(color="orange", linestyle=":", label="power law troncata")
plt.xlabel("Grado (k)"); plt.ylabel("P(K ≥ k)"); plt.legend()
plt.title(f"Coda della distribuzione del grado (k ≥ {fit.xmin:.0f})")
plt.tight_layout(); plt.savefig(PLOT_NA / "grado_ccdf_fit.png", dpi=150); plt.close()

# figura nello stile del notebook del corso: P(k), CDF e CCDF con i fit
fig, ax = plt.subplots(1, 3, figsize=(15, 4.5))
c = Counter(gradi); k = sorted(c)
ax[0].scatter(k, [c[x] for x in k], s=8, color="blue")
ax[0].set_xscale("log"); ax[0].set_yscale("log")
ax[0].set_xlabel("Degree"); ax[0].set_ylabel("P(k)")
fit.plot_cdf(ax=ax[1], original_data=True)
ax[1].set_xlabel("Degree"); ax[1].set_ylabel("CDF")
fit.plot_ccdf(ax=ax[2], label="data (k >= k_min)")
fit.power_law.plot_ccdf(ax=ax[2], color="r", linestyle="--", label=f"power law (alpha={fit.alpha:.2f})")
fit.lognormal.plot_ccdf(ax=ax[2], color="seagreen", label="lognormal")
ax[2].set_xlabel("Degree"); ax[2].set_ylabel("CCDF"); ax[2].legend()
plt.tight_layout(); plt.savefig(PLOT_NA / "grado_distribuzione.png", dpi=150); plt.close()
print("\nSalvati: grado_lineare.png, grado_loglog.png, grado_ccdf_fit.png, gradi.json")
