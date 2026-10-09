"""PARTE 1 - Costruisce la rete finale: sottografo indotto sui soli nodi ESPANSI con successo
(per ogni nodo della rete conosciamo tutte le raccomandazioni in uscita).
Uscita (dataset finale, in data/):
  archi.csv  sorgente, destinazione, reciproca   (una riga per raccomandazione: sorgente -> destinazione)
  nodi.csv   url, seed, out_degree, in_degree    (una riga per newsletter; gli attributi tematici e le
             comunita' vengono aggiunti alla fine da open_problem/10_esporta_rete.py)"""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from comune import DATA, RACCOLTA, SEED
import pandas as pd

df = pd.read_csv(RACCOLTA / "raccomandazioni_grezze.csv", names=["sorgente", "destinazione"]).drop_duplicates()
stato = json.load(open(RACCOLTA / "stato_crawl.json"))
falliti = set(stato.get("falliti", []))
espansi = set(stato["espansi"]) - falliti        # esclusi i nodi con richiesta fallita

print(f"Raccomandazioni grezze raccolte: {len(df)}")
print(f"Nodi scoperti (noti):            {len(stato['noti'])}")
print(f"Nodi espansi con successo:       {len(espansi)}")
print(f"Nodi falliti (esclusi):          {len(falliti)}")

archi = df[df.sorgente.isin(espansi) & df.destinazione.isin(espansi)
           & (df.sorgente != df.destinazione)].sort_values(["sorgente", "destinazione"])
coppie = set(zip(archi.sorgente, archi.destinazione))
archi["reciproca"] = [int((t, s) in coppie) for s, t in zip(archi.sorgente, archi.destinazione)]

nodi = pd.DataFrame({"url": sorted(espansi)})
nodi["seed"] = nodi.url.isin(SEED).astype(int)
nodi["out_degree"] = nodi.url.map(archi.sorgente.value_counts()).fillna(0).astype(int)
nodi["in_degree"] = nodi.url.map(archi.destinazione.value_counts()).fillna(0).astype(int)

print("\n--- rete finale ---")
print(f"Nodi: {len(nodi)} (di cui seed: {nodi.seed.sum()})")
print(f"Archi diretti: {len(archi)} | reciproci: {archi.reciproca.mean():.3f}")
print(f"Nodi senza raccomandazioni in uscita verso la rete: {(nodi.out_degree == 0).sum()}")
print(f"Out-degree massimo: {nodi.out_degree.max()} (tetto della piattaforma: 50)")

archi.to_csv(DATA / "archi.csv", index=False)
nodi.to_csv(DATA / "nodi.csv", index=False)
print("\nSalvati data/archi.csv e data/nodi.csv")
