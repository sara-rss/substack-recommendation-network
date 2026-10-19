"""Parte 4.5: Missing label

Si analizza come sono distribuite le label mancanti 

Controlli:
- perché manca la label
- dove stanno nella rete
- se sono sparse tra le comunità o concentrate in alcune
- se un nodo senza label cade in una comunità con un tema dominante, e quanto ci si può
  fidare: lo stimo sui nodi con label, nascondendola e guardando se coincide col tema
  dominante della comunità
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import csv
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from collections import Counter, defaultdict
from scipy.stats import chi2_contingency, mannwhitneyu
from comune import carica_grafo, carica_attributi, carica_comunita, PLOT_OP

MIN_NODI = 100                       # soglia per le comunità principali
SOGLIE_PUREZZA = [0.5, 0.6, 0.7, 0.8]

# perché manca la label
TIPO = {
    "senza_testo": "senza testo", "generic": "titoli generici", "non_english": "altra lingua",
    "media_video": "video/podcast", "coming_soon": "titoli generici", "date_only": "titoli generici",
    "portuguese": "altra lingua", "spanish": "altra lingua",
}

G = carica_grafo(); tema, macro = carica_attributi(); com = carica_comunita()
nodi = list(G)


# "label" se il nodo ha un tema utile, altrimenti il motivo per cui manca
def stato(u):
    if u not in tema:
        return "senza testo"
    if macro[u] == "unlabeled":
        return TIPO.get(tema[u], "titoli generici")
    return "label"


st = {u: stato(u) for u in nodi}
manca = {u for u in nodi if st[u] != "label"}
N = len(nodi)


# quanti nodi senza label e perché
print(f"=== A. COMPOSIZIONE ===\nNodi: {N} | con label: {N - len(manca)} | "
      f"senza label: {len(manca)} ({100*len(manca)/N:.1f}%)")
for t, n in Counter(st[u] for u in manca).most_common():
    print(f"  {t:16} {n:6} ({100*n/N:.1f}% della rete)")
# i "personal" hanno una label ma contano poco
vaghe = sum(1 for u in nodi if tema.get(u) == "personal")
print(f"  (a parte: {vaghe} nodi 'personal' hanno una label ma vaga, {100*vaghe/N:.1f}%)")


# confronto il grado di chi ha la label e di chi non ce l'ha
print("\n=== B. POSIZIONE NELLA RETE ===")
g_lab = np.array([G.degree(u) for u in nodi if u not in manca])
g_man = np.array([G.degree(u) for u in manca])
p = mannwhitneyu(g_man, g_lab, alternative="less").pvalue  
print(f"Grado mediano: con label {np.median(g_lab):.0f} | senza label {np.median(g_man):.0f} "
      f"(Mann-Whitney, senza < con: p = {p:.1e})")
print(f"Grado medio:   con label {g_lab.mean():.1f} | senza label {g_man.mean():.1f}")

# quota di nodi senza label in ogni fascia di grado
print("Quota di nodi senza label per fascia di grado:")
fasce = [(1, 1), (2, 3), (4, 6), (7, 12), (13, 25), (26, 50), (51, 10**6)]
x_f, y_f = [], []
for lo, hi in fasce:
    gruppo = [u for u in nodi if lo <= G.degree(u) <= hi]
    q = sum(u in manca for u in gruppo) / len(gruppo)
    et = f"{lo}" if lo == hi else (f"{lo}-{hi}" if hi < 10**6 else f"{lo}+")
    x_f.append(et); y_f.append(100 * q)
    print(f"  grado {et:>6}: {100*q:5.1f}%  ({len(gruppo)} nodi)")
tipi = sorted({st[u] for u in manca})
print("Grado mediano per tipo di label mancante:",
      ", ".join(f"{t} {np.median([G.degree(u) for u in manca if st[u] == t]):.0f}" for t in tipi))

# ---- figura per il report ----
ORDINE = [("senza testo", "No text", "#2a78d6"),
          ("titoli generici", "Generic titles", "#eb6834"),
          ("altra lingua", "Non-English", "#1baf7a"),
          ("video/podcast", "Video / podcast", "#eda100")]
media = 100 * len(manca) / N
quote = {t: [] for t, _, _ in ORDINE}
n_f = []
for lo, hi in fasce:
    gruppo = [u for u in nodi if lo <= G.degree(u) <= hi]
    n_f.append(len(gruppo))
    for t, _, _ in ORDINE:
        quote[t].append(100 * sum(st[u] == t for u in gruppo) / len(gruppo))

INK, INK2, GRIGIO = "#0b0b0b", "#52514e", "#e4e3df"
plt.rcParams.update({"font.size": 8, "axes.edgecolor": INK2, "xtick.color": INK2, "ytick.color": INK2})
fig, ax = plt.subplots(figsize=(3.4, 2.6))
x = np.arange(len(fasce))
base = np.zeros(len(fasce))
for t, nome, col in ORDINE:
    ax.bar(x, quote[t], bottom=base, width=0.7, color=col, edgecolor="white",
           linewidth=0.8, label=nome, zorder=3)
    base += np.array(quote[t])
for i, tot in enumerate(y_f):                     
    ax.text(i, tot + 0.8, f"{tot:.0f}%", ha="center", va="bottom", fontsize=7, color=INK,
            zorder=5, bbox=dict(facecolor="white", edgecolor="none", pad=0.6))

ax.axhline(media, color=INK2, linestyle=(0, (4, 3)), linewidth=0.9, zorder=4)
ax.text(len(fasce) - 0.55, media + 0.8, f"network average {media:.1f}%",
        ha="right", va="bottom", fontsize=7, color=INK2)

ax.set_xticks(x)
ax.set_xticklabels([f"{e.replace('-', '–')}\n{n:,}" for e, n in zip(x_f, n_f)], fontsize=7)
ax.text(-0.75, -0.083, "n =", transform=ax.get_xaxis_transform(),
        ha="right", va="top", fontsize=7, color=INK2)
ax.set_xlabel("Degree", labelpad=4)
ax.set_ylabel("Newsletters without a topic (%)")
ax.set_ylim(0, max(y_f) * 1.18); ax.set_xlim(-0.6, len(fasce) - 0.4)
ax.yaxis.grid(True, color=GRIGIO, linewidth=0.6, zorder=0)
ax.spines[["top", "right"]].set_visible(False); ax.tick_params(length=0)
ax.legend(loc="upper center", bbox_to_anchor=(0.5, 1.17), ncol=4, frameon=False, fontsize=6.5,
          handlelength=1, handletextpad=0.4, columnspacing=0.9)
plt.savefig(PLOT_OP / "label_mancanti_grado.png", dpi=300, bbox_inches="tight"); plt.close()

# ---------------- distribuzione tra le comunità ----------------
print("\n=== C. DISTRIBUZIONE TRA LE COMUNITÀ ===")
membri = defaultdict(list)
for u in nodi:
    membri[com[u]].append(u)
grandi = sorted((c for c in membri if len(membri[c]) >= MIN_NODI), key=lambda c: -len(membri[c]))

# tabella comunità 
# se le label mancanti fossero sparse a caso la quota sarebbe simile in tutte le comunità
tab = np.array([[sum(st[u] == "label" for u in membri[c]), sum(st[u] != "label" for u in membri[c])]
                for c in grandi])
chi2, p, dof, _ = chi2_contingency(tab)
# V di Cramer: quanto è forte l'associazione 
v = np.sqrt(chi2 / tab.sum())
print(f"Chi quadro (label mancante x comunità, {len(grandi)} comunità principali): "
      f"chi2 = {chi2:.0f}, p = {p:.1e}, V di Cramer = {v:.2f}")


# tema dominante di una comunità e sua purezza con solo i nodi con label
def profilo(c):
    lab = Counter(macro[u] for u in membri[c] if st[u] == "label")
    if not lab:
        return "-", 0.0
    t, n = lab.most_common(1)[0]
    return t, n / sum(lab.values())


# per ogni comunità principale: quota senza label, tema dominante e motivi più frequenti
righe = []
print(f"\n{'com':>4} {'nodi':>6} {'senza label':>12}   tema dominante (purezza sui nodi con label)   tipi di mancanza")
for c in grandi:
    m = [u for u in membri[c] if st[u] != "label"]
    dom, pur = profilo(c)
    tipi_c = Counter(st[u] for u in m)
    print(f"{c:>4} {len(membri[c]):>6} {100*len(m)/len(membri[c]):>11.1f}%   {dom:18} ({100*pur:3.0f}%)"
          f"          {', '.join(f'{t} {n}' for t, n in tipi_c.most_common(3))}")
    righe.append([c, len(membri[c]), len(m), round(len(m) / len(membri[c]), 3), dom, round(pur, 3)]
                 + [tipi_c.get(t, 0) for t in tipi])
piccole = [u for c in membri if c not in grandi for u in membri[c]]
if piccole:
    print(f"comunità marginali: {len(piccole)} nodi, senza label "
          f"{100*sum(st[u] != 'label' for u in piccole)/len(piccole):.1f}%")
with open(PLOT_OP / "label_mancanti_per_comunita.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["comunita", "n_nodi", "n_senza_label", "quota_senza_label", "tema_dominante", "purezza"]
               + [f"n_{t.replace(' ', '_')}" for t in tipi])
    w.writerows(righe)


# ---------------- associazione a livello di comunità ----------------
print("\n=== D. SI PUÒ ASSOCIARE UN TEMA AI NODI SENZA LABEL TRAMITE LA LORO COMUNITÀ? ===")
print("(stima di affidabilità sui nodi CON label: nascondo la loro label e confronto con il tema")
print(" dominante della loro comunità, calcolato senza di loro)")
# solo comunità principali: in quelle minuscole togliere un nodo cambia molto la purezza
conta = {c: Counter(macro[u] for u in membri[c] if st[u] == "label") for c in membri}
esiti = []                                   
for u in nodi:
    if st[u] != "label" or com[u] not in grandi:
        continue
    # tolgo il nodo dal conteggio della sua comunità e guardo se il tema dominante resta il suo
    cnt = conta[com[u]].copy(); cnt[macro[u]] -= 1
    tot = sum(cnt.values())
    if tot == 0:
        continue
    t, n = cnt.most_common(1)[0]
    esiti.append((n / tot, t == macro[u]))
esiti = np.array(esiti, float)

# due valori di confronto: quanto si indovinerebbe a caso e quanto scegliendo sempre il tema più comune
freq = np.array(list(Counter(macro[u] for u in nodi if st[u] == "label").values()), float)
freq /= freq.sum()
print(f"Accordo complessivo: {100*esiti[:, 1].mean():.1f}%  "
      f"(riferimento casuale: {100*(freq**2).sum():.1f}%; tema più frequente: {100*freq.max():.1f}%)")
print(f"(solo le {len(grandi)} comunità principali)")

# per ogni soglia di purezza: quanto spesso il tema della comunità è giusto e quanti nodi senza label ne fanno parte
print(f"\n{'purezza comunità':>18} {'accordo sui nodi con label':>28} {'nodi senza label coinvolti':>28}")
for soglia in SOGLIE_PUREZZA:
    sel = esiti[esiti[:, 0] >= soglia]
    n_man = sum(1 for u in manca if com[u] in grandi and profilo(com[u])[1] >= soglia)
    acc = f"{100*sel[:, 1].mean():.1f}% su {len(sel)}" if len(sel) >= 30 else "n.d. (troppo pochi)"
    print(f"{'>= ' + str(int(100*soglia)) + '%':>18} {acc:>28} {n_man:>18} ({100*n_man/len(manca):.0f}%)")
print("\nLettura: nelle comunità molto pure il tema della comunità è un'indicazione affidabile")
print("anche per i nodi senza label; nelle comunità miste no. Resta un'indicazione a margine,")
print("non una riclassificazione: nessuna label viene assegnata e le analisi principali usano")
print("solo le label ricavate dal testo.")