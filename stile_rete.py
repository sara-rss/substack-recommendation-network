"""Stile condiviso della rete: nomi inglesi, colori e dimensioni dei nodi, così Gephi e la figura mostrano esattamente gli stessi colori e la stessa legenda."""

# Una riga per comunità, le righe sono nell'ordine in cui compaiono nella legenda
COMUNITA = [
    ("startup / tech / AI (costruire)",            "Start-ups & technology",    "#2B7BC4"),
    ("literary & personal essay",                  "Literary & personal essay", "#E3328C"),
    ("investing (mercati finanziari)",             "Investing",                 "#C48A12"),
    ("food, fashion & home",                       "Food, fashion & home",      "#1E9E6E"),
    ("liberal mainstream",                         "Liberal mainstream",        "#E5473B"),
    ("heterodox-centrist / policy",                "Heterodox-centrist",        "#8E4FB0"),
    ("anti-establishment / anti-interventionist",  "Anti-establishment",        "#6AA22C"),
    ("health & science",                           "Health & science",          "#222222"),
    ("music / film / pop culture",                 "Music, film & pop culture", "#0F8F95"),
    ("eterogenea (nessun tema dominante)",         "Heterogeneous",             "#8C564B"),
    ("marginale",                                  "Other (marginal)",          "#BDBDBD"),
]
NOME_EN = {it: en for it, en, _ in COMUNITA}
COLORE = {it: c for it, _, c in COMUNITA}

# Dimensione dei nodi: radice del grado, compressa fra DIM_MIN e DIM_MAX (unita' di Gephi).
DIM_MIN, DIM_MAX = 1.5, 14.0
def dimensione_nodo(grado, grado_max):
    return DIM_MIN + (DIM_MAX - DIM_MIN) * ((grado - 1) / (grado_max - 1)) ** 0.5

def rgb(hex_colore):
    h = hex_colore.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))

# Layout: ForceAtlas2 di Gephi
FILE_POSIZIONI = "posizioni_fa2.csv"

OPACITA_ARCHI = 0.20      # alpha degli archi nella figura matplotlib
