"""PARTE 4.4 - Comunità principali: dimensione, temi, newsletter
più centrali, quota di archi interni"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import csv
from collections import Counter, defaultdict
from comune import carica_grafo, carica_attributi, carica_comunita, corto, PLOT_OP

# un'ancora è un macro-ambito, etichetta data a mano dopo aver guardato la comunità
# Da ricontrollare se si rilancia 05_comunita: due ancore nella stessa comunità vengono
# segnalate, le comunità senza ancora prendono ETICHETTA_MISTA
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
# etichetta per le comunità principali che non contengono nessuna ancora
ETICHETTA_MISTA = ("mixed", "eterogenea (nessun tema dominante)")
MIN_NODI = 100
G = carica_grafo(); tema, macro = carica_attributi(); com = carica_comunita()

# comunità -> lista dei suoi nodi
membri = defaultdict(list)
for u, c in com.items():
    membri[c].append(u)

# assegno le etichette: ogni ancora dà il suo nome alla comunità in cui è finita.
etichetta = {}
for a, et in ANCORE.items():
    a = a.replace("://www.", "://")
    if a in com and com[a] in etichetta and etichetta[com[a]] != et:
        # due ancore nella stessa comunità, unisco le etichette
        print(f"NOTA: '{et[1]}' e '{etichetta[com[a]][1]}' cadono nella stessa comunità ({com[a]})")
        v = etichetta[com[a]]
        etichetta[com[a]] = (v[0] if v[0] == et[0] else v[0] + "+" + et[0], v[1] + "  +  " + et[1])
    elif a in com:
        etichetta[com[a]] = et
    else:
        print("ATTENZIONE: ancora non trovata nella rete:", a)

# profilo di ogni comunità principale, dalla più grande
righe, righe_et = [], []
for c in sorted(membri, key=lambda c: -len(membri[c])):
    n = len(membri[c])
    if n < MIN_NODI:
        continue
    S = G.subgraph(membri[c])

    # somma dei gradi 
    interni = S.number_of_edges()
    totali = sum(G.degree(u) for u in membri[c]) - interni

    # temi e macro-tema dominante 
    tf = Counter(tema.get(u, "senza_testo") for u in membri[c])
    ut = Counter(macro[u] for u in membri[c] if macro.get(u, "unlabeled") != "unlabeled")
    dom, ndom = ut.most_common(1)[0]

    # le 8 newsletter con più collegamenti dentro la comunità 
    top = [corto(u) for u, _ in sorted(S.degree(), key=lambda x: -x[1])[:8]]
    amb, et = etichetta.get(c, ETICHETTA_MISTA)

    print(f"\n=== comunità {c}: {n} nodi | {et} ===")
    print(f"  archi interni: {100*interni/totali:.0f}% | macro dominante: {dom} "
          f"({100*ndom/sum(ut.values()):.0f}% dei nodi etichettati)")
    print("  temi fini:", ", ".join(f"{t} {100*v/n:.0f}%" for t, v in tf.most_common(5)))
    print("  più centrali:", ", ".join(top))
    righe.append([c, n, et, round(interni / totali, 3), dom, round(ndom / sum(ut.values()), 3),
                  "; ".join(f"{t} {100*v/n:.0f}%" for t, v in tf.most_common(5)), "; ".join(top)])
    righe_et.append([c, n, amb, et])

# quante comunità restano fuori
piccole = [len(m) for m in membri.values() if len(m) < MIN_NODI]
print(f"\nComunità marginali (<{MIN_NODI} nodi): {len(piccole)}, in tutto {sum(piccole)} nodi "
      f"({100*sum(piccole)/len(com):.1f}%)")

# purezza = quota del macro-tema dominante tra i nodi etichettati della comunità
with open(PLOT_OP / "comunita_profilo.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["comunita", "n_nodi", "etichetta", "quota_archi_interni", "macro_dominante",
                "purezza", "temi_fini", "newsletter_centrali"]); w.writerows(righe)
with open(PLOT_OP / "comunita_etichette.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["comunita", "n_nodi", "ambito", "etichetta"]); w.writerows(righe_et)

# per ogni macro-tema come si divide tra le comunità 
print("\n=== in quali comunità si distribuisce ogni macro-tema (quote >= 10%) ===")
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