"""PARTE 1 - Costruisce la rete: sottografo sui soli nodi espansi con successo
Un arco viene tenuto solo se sia la sorgente sia la destinazione sono state espanse"""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from comune import DATA, RACCOLTA, SEED
import pandas as pd

# Carico gli archi grezzi del crawl e lo stato finale
df = pd.read_csv(RACCOLTA / "raccomandazioni_grezze.csv", names=["sorgente", "destinazione"]).drop_duplicates()
stato = json.load(open(RACCOLTA / "stato_crawl.json"))
falliti = set(stato.get("falliti", []))
espansi = set(stato["espansi"]) - falliti   # escludo i nodi con richiesta fallita

print(f"Raccomandazioni grezze raccolte: {len(df)}")
print(f"Nodi scoperti (noti):            {len(stato['noti'])}")
print(f"Nodi espansi con successo:       {len(espansi)}")
print(f"Nodi falliti (esclusi):          {len(falliti)}")

# Archi tra nodi espansi, senza self-loop, ordinati per sorgente e destinazione
archi = df[df.sorgente.isin(espansi) & df.destinazione.isin(espansi)
           & (df.sorgente != df.destinazione)].sort_values(["sorgente", "destinazione"])

# reciproca = 1 se esiste anche l'arco inverso (B -> A), altrimenti 0
coppie = set(zip(archi.sorgente, archi.destinazione))
archi["reciproca"] = [int((t, s) in coppie) for s, t in zip(archi.sorgente, archi.destinazione)]

# Tabella dei nodi: seed sì/no e numero di archi in uscita e in entrata dentro la rete
nodi = pd.DataFrame({"url": sorted(espansi)})
nodi["seed"] = nodi.url.isin(SEED).astype(int)
nodi["out_degree"] = nodi.url.map(archi.sorgente.value_counts()).fillna(0).astype(int)
nodi["in_degree"] = nodi.url.map(archi.destinazione.value_counts()).fillna(0).astype(int)

print("\n--- rete finale ---")
print(f"Nodi: {len(nodi)} (di cui seed: {nodi.seed.sum()})")
print(f"Archi diretti: {len(archi)} | quota reciproci: {archi.reciproca.mean():.3f}")
print(f"Nodi senza raccomandazioni in uscita verso la rete: {(nodi.out_degree == 0).sum()}")
print(f"Out-degree massimo: {nodi.out_degree.max()} (tetto della piattaforma: 50)")

archi.to_csv(DATA / "archi.csv", index=False)
nodi.to_csv(DATA / "nodi.csv", index=False)
print("\nSalvati data/archi.csv e data/nodi.csv")