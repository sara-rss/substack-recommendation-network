"""PARTE 4.5 - Analisi delle LABEL MANCANTI (discussione a margine, NON riclassificazione).
Una parte dei nodi non ha un tema ricavabile dal testo. Qui non si prova ad assegnarglielo:
si studia COME sono distribuite le label mancanti, per capire se introducono una distorsione
nei risultati. Nessun file prodotto qui viene usato dagli altri script.

 A. Composizione: perche' manca la label (senza testo, titoli generici, altra lingua, video...).
 B. Posizione nella rete: i nodi senza label sono periferici (grado basso) o anche hub?
 C. Distribuzione tra le comunita': le label mancanti sono sparse uniformemente o concentrate
    in alcune comunita'? (test del chi quadro). Se sono concentrate, le comunita' interessate
    sono descritte peggio delle altre e il legame comunita'-tema e' stimato con meno dati.
 D. Associazione a livello di comunita': un nodo senza label cade in una comunita' con un tema
    nettamente dominante? Quanto e' affidabile questa associazione? La si stima sui nodi CON
    label (si nasconde la loro label e si guarda se il tema dominante della comunita' coincide).
    E' un'indicazione di quanto la struttura della rete "contenga" l'informazione mancante,
    non un'assegnazione di tema.
Uscita: plots/label_mancanti_per_comunita.csv, plots/label_mancanti_comunita.png,
        plots/label_mancanti_grado.png"""
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

MIN_NODI = 100                       # comunita' "principali"
SOGLIE_PUREZZA = [0.5, 0.6, 0.7, 0.8]
TIPO = {                             # perche' manca la label
    "senza_testo": "senza testo", "generic": "titoli generici", "non_english": "altra lingua",
    "media_video": "video/podcast", "coming_soon": "titoli generici", "date_only": "titoli generici",
    "portuguese": "altra lingua", "spanish": "altra lingua",
}

G = carica_grafo(); tema, macro = carica_attributi(); com = carica_comunita()
nodi = list(G)


def stato(u):
    """'label' | tipo di label mancante"""
    if u not in tema:
        return "senza testo"
    if macro[u] == "unlabeled":
        return TIPO.get(tema[u], "titoli generici")
    return "label"


st = {u: stato(u) for u in nodi}
manca = {u for u in nodi if st[u] != "label"}
N = len(nodi)

# ---------------- A. composizione ----------------
print(f"=== A. COMPOSIZIONE ===\nNodi: {N} | con label: {N - len(manca)} | "
      f"senza label: {len(manca)} ({100*len(manca)/N:.1f}%)")
for t, n in Counter(st[u] for u in manca).most_common():
    print(f"  {t:16} {n:6} ({100*n/N:.1f}% della rete)")
vaghe = sum(1 for u in nodi if tema.get(u) == "personal")
print(f"  (a parte: {vaghe} nodi 'personal' hanno una label ma vaga, {100*vaghe/N:.1f}%)")

# ---------------- B. posizione nella rete ----------------
print("\n=== B. POSIZIONE NELLA RETE ===")
g_lab = np.array([G.degree(u) for u in nodi if u not in manca])
g_man = np.array([G.degree(u) for u in manca])
p = mannwhitneyu(g_man, g_lab, alternative="less").pvalue
print(f"Grado mediano: con label {np.median(g_lab):.0f} | senza label {np.median(g_man):.0f} "
      f"(Mann-Whitney, senza < con: p = {p:.1e})")
print(f"Grado medio:   con label {g_lab.mean():.1f} | senza label {g_man.mean():.1f}")
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

plt.figure(figsize=(6, 4))
plt.bar(x_f, y_f, color="gray")
plt.axhline(100 * len(manca) / N, color="crimson", linestyle="--", label="media della rete")
plt.xlabel("Grado"); plt.ylabel("% di nodi senza label"); plt.legend()
plt.title("Label mancanti per fascia di grado")
plt.tight_layout(); plt.savefig(PLOT_OP / "label_mancanti_grado.png", dpi=150); plt.close()

# ---------------- C. distribuzione tra le comunita' ----------------
print("\n=== C. DISTRIBUZIONE TRA LE COMUNITA' ===")
membri = defaultdict(list)
for u in nodi:
    membri[com[u]].append(u)
grandi = sorted((c for c in membri if len(membri[c]) >= MIN_NODI), key=lambda c: -len(membri[c]))
tab = np.array([[sum(st[u] == "label" for u in membri[c]), sum(st[u] != "label" for u in membri[c])]
                for c in grandi])
chi2, p, dof, _ = chi2_contingency(tab)
# V di Cramer: intensita' dell'associazione (0 = nessuna, 1 = massima)
v = np.sqrt(chi2 / tab.sum())
print(f"Chi quadro (label mancante x comunita', {len(grandi)} comunita' principali): "
      f"chi2 = {chi2:.0f}, p = {p:.1e}, V di Cramer = {v:.2f}")


def profilo(c):
    lab = Counter(macro[u] for u in membri[c] if st[u] == "label")
    if not lab:
        return "-", 0.0
    t, n = lab.most_common(1)[0]
    return t, n / sum(lab.values())


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
    print(f"comunita' marginali: {len(piccole)} nodi, senza label "
          f"{100*sum(st[u] != 'label' for u in piccole)/len(piccole):.1f}%")
with open(PLOT_OP / "label_mancanti_per_comunita.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["comunita", "n_nodi", "n_senza_label", "quota_senza_label", "tema_dominante", "purezza"]
               + [f"n_{t.replace(' ', '_')}" for t in tipi])
    w.writerows(righe)

# grafico: quota di label mancanti per comunita', divisa per tipo
fig, ax = plt.subplots(figsize=(9, 4.5))
base = np.zeros(len(grandi))
colori = plt.cm.Set2(np.arange(len(tipi)))
for t, col in zip(tipi, colori):
    val = np.array([100 * sum(st[u] == t for u in membri[c]) / len(membri[c]) for c in grandi])
    ax.bar([str(c) for c in grandi], val, bottom=base, label=t, color=col); base += val
ax.axhline(100 * len(manca) / N, color="crimson", linestyle="--", label="media della rete")
ax.set_xticks(range(len(grandi)))
ax.set_xticklabels([f"{c}\n{profilo(c)[0][:10]}" for c in grandi], fontsize=7)
ax.set_ylabel("% di nodi senza label"); ax.legend(fontsize=7)
ax.set_title("Label mancanti nelle comunita' principali (sotto: tema dominante)")
plt.tight_layout(); plt.savefig(PLOT_OP / "label_mancanti_comunita.png", dpi=150); plt.close()

# ---------------- D. associazione a livello di comunita' ----------------
print("\n=== D. SI PUO' ASSOCIARE UN TEMA AI NODI SENZA LABEL TRAMITE LA LORO COMUNITA'? ===")
print("(stima di affidabilita' sui nodi CON label: nascondo la loro label e confronto con il tema")
print(" dominante della loro comunita', calcolato senza di loro)")
# solo comunita' principali: in quelle minuscole togliere un nodo cambia molto la purezza
# e la stima "lascia fuori un nodo" diventa distorta
conta = {c: Counter(macro[u] for u in membri[c] if st[u] == "label") for c in membri}
esiti = []                                   # (purezza della comunita', indovinato?)
for u in nodi:
    if st[u] != "label" or com[u] not in grandi:
        continue
    cnt = conta[com[u]].copy(); cnt[macro[u]] -= 1
    tot = sum(cnt.values())
    if tot == 0:
        continue
    t, n = cnt.most_common(1)[0]
    esiti.append((n / tot, t == macro[u]))
esiti = np.array(esiti, float)
freq = np.array(list(Counter(macro[u] for u in nodi if st[u] == "label").values()), float)
freq /= freq.sum()
print(f"Accordo complessivo: {100*esiti[:, 1].mean():.1f}%  "
      f"(riferimento casuale: {100*(freq**2).sum():.1f}%; tema piu' frequente: {100*freq.max():.1f}%)")
print(f"(solo le {len(grandi)} comunita' principali)")
print(f"\n{'purezza comunita':>18} {'accordo sui nodi con label':>28} {'nodi senza label coinvolti':>28}")
for soglia in SOGLIE_PUREZZA:
    sel = esiti[esiti[:, 0] >= soglia]
    n_man = sum(1 for u in manca if com[u] in grandi and profilo(com[u])[1] >= soglia)
    acc = f"{100*sel[:, 1].mean():.1f}% su {len(sel)}" if len(sel) >= 30 else "n.d. (troppo pochi)"
    print(f"{'>= ' + str(int(100*soglia)) + '%':>18} {acc:>28} {n_man:>18} ({100*n_man/len(manca):.0f}%)")
print("\nLettura: nelle comunita' molto pure il tema della comunita' e' un'indicazione affidabile")
print("anche per i nodi senza label; nelle comunita' miste no. Resta un'indicazione a margine,")
print("non una riclassificazione: nessuna label viene assegnata e le analisi principali usano")
print("solo le label ricavate dal testo.")
