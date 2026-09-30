"""PARTE 4.4 - Carta d'identita' di TUTTE le comunita' principali: dimensione, temi, newsletter
piu' centrali, densita' interna. Le etichette interpretative sono agganciate a una newsletter
"ancora" (non al numero della comunita', che cambia se la rete cambia).
Uscita: plots/comunita_profilo.csv, plots/comunita_etichette.csv, plots/temi_per_comunita.csv"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import csv
from collections import Counter, defaultdict
from comune import carica_grafo, carica_attributi, carica_comunita, corto, PLOT_OP

# ancora -> (macro-ambito, etichetta interpretativa data dopo ispezione manuale).
# DA RICONTROLLARE dopo ogni nuova esecuzione di 05_comunita.py: se due ancore cadono nella
# stessa comunita' lo script lo segnala (NOTA); le comunita' principali senza ancora ricevono
# l'etichetta ETICHETTA_MISTA: controllare le newsletter centrali stampate per decidere se serve
# un'ancora nuova.
ANCORE = {
    "https://chrishedges.substack.com":             ("politics", "anti-establishment / anti-interventionist"),
    "https://www.noahpinion.blog":                  ("politics", "heterodox-centrist / policy"),
    "https://heathercoxrichardson.substack.com":    ("politics", "liberal mainstream"),
    "https://capitalwars.substack.com":             ("markets", "investing (mercati finanziari)"),
    "https://www.lennysnewsletter.com":             ("builders", "startup / tech / AI (costruire)"),
    "https://georgesaunders.substack.com":          ("writing", "literary & personal essay"),
    "https://davidlebovitz.substack.com":           ("lifestyle", "food, fashion & home"),
    "https://yourlocalepidemiologist.substack.com": ("science", "health & science"),
    "https://thekevinalexander.substack.com":       ("culture", "music / film / pop culture"),
}
# comunita' principali senza un tema dominante chiaro (nessuna ancora): etichetta generica
ETICHETTA_MISTA = ("mixed", "eterogenea (nessun tema dominante)")
MIN_NODI = 100
G = carica_grafo(); tema, macro = carica_attributi(); com = carica_comunita()
membri = defaultdict(list)
for u, c in com.items():
    membri[c].append(u)

etichetta = {}
for a, et in ANCORE.items():
    a = a.replace("://www.", "://")
    if a in com and com[a] in etichetta and etichetta[com[a]] != et:
        # due ancore nella stessa comunita': in questa partizione i due gruppi NON sono separati
        print(f"NOTA: '{et[1]}' e '{etichetta[com[a]][1]}' cadono nella stessa comunita' ({com[a]})")
        v = etichetta[com[a]]
        etichetta[com[a]] = (v[0] if v[0] == et[0] else v[0] + "+" + et[0], v[1] + "  +  " + et[1])
    elif a in com:
        etichetta[com[a]] = et
    else:
        print("ATTENZIONE: ancora non trovata nella rete:", a)

righe, righe_et = [], []
for c in sorted(membri, key=lambda c: -len(membri[c])):
    n = len(membri[c])
    if n < MIN_NODI:
        continue
    S = G.subgraph(membri[c])
    interni = S.number_of_edges()
    totali = sum(G.degree(u) for u in membri[c]) - interni
    tf = Counter(tema.get(u, "senza_testo") for u in membri[c])
    ut = Counter(macro[u] for u in membri[c] if macro.get(u, "unlabeled") != "unlabeled")
    dom, ndom = ut.most_common(1)[0]
    top = [corto(u) for u, _ in sorted(S.degree(), key=lambda x: -x[1])[:8]]
    amb, et = etichetta.get(c, ETICHETTA_MISTA)
    print(f"\n=== comunita' {c}: {n} nodi | {et} ===")
    print(f"  archi interni: {100*interni/totali:.0f}% | macro dominante: {dom} "
          f"({100*ndom/sum(ut.values()):.0f}% dei nodi etichettati)")
    print("  temi fini:", ", ".join(f"{t} {100*v/n:.0f}%" for t, v in tf.most_common(5)))
    print("  piu' centrali:", ", ".join(top))
    righe.append([c, n, et, round(interni / totali, 3), dom, round(ndom / sum(ut.values()), 3),
                  "; ".join(f"{t} {100*v/n:.0f}%" for t, v in tf.most_common(5)), "; ".join(top)])
    righe_et.append([c, n, amb, et])

piccole = [len(m) for m in membri.values() if len(m) < MIN_NODI]
print(f"\nComunita' marginali (<{MIN_NODI} nodi): {len(piccole)}, in tutto {sum(piccole)} nodi "
      f"({100*sum(piccole)/len(com):.1f}%)")

with open(PLOT_OP / "comunita_profilo.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["comunita", "n_nodi", "etichetta", "quota_archi_interni", "macro_dominante",
                "purezza", "temi_fini", "newsletter_centrali"]); w.writerows(righe)
with open(PLOT_OP / "comunita_etichette.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["comunita", "n_nodi", "ambito", "etichetta"]); w.writerows(righe_et)

# tabella temi x comunita': in quante comunita' si spezza ogni macro-tema?
print("\n=== in quali comunita' si distribuisce ogni macro-tema (quote >= 10%) ===")
per_tema = defaultdict(Counter)
for u, c in com.items():
    if macro.get(u, "unlabeled") != "unlabeled":
        per_tema[macro[u]][c] += 1
with open(PLOT_OP / "temi_per_comunita.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["macro", "comunita", "n_nodi", "quota"])
    for m, cnt in sorted(per_tema.items()):
        tot = sum(cnt.values())
        print(f"  {m:18}", ", ".join(f"com {c}: {100*v/tot:.0f}%" for c, v in cnt.most_common() if v / tot >= 0.10))
        for c, v in cnt.most_common():
            w.writerow([m, c, v, round(v / tot, 3)])
