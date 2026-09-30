"""PARTE 1 - Costruisce la rete finale: sottografo indotto sui soli nodi ESPANSI con successo
(per ogni nodo della rete conosciamo tutte le raccomandazioni in uscita).
Uscita: data/rete_finale.csv (archi diretti) e data/nodi_finali.csv."""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from comune import DATA
import pandas as pd

df = pd.read_csv(DATA / "archi.csv", names=["sorgente", "destinazione"]).drop_duplicates()
stato = json.load(open(DATA / "stato.json"))
falliti = set(stato.get("falliti", []))
espansi = set(stato["espansi"]) - falliti        # esclusi i nodi con richiesta fallita

print(f"Archi grezzi raccolti:        {len(df)}")
print(f"Nodi scoperti (noti):         {len(stato['noti'])}")
print(f"Nodi espansi con successo:    {len(espansi)}")
print(f"Nodi falliti (esclusi):       {len(falliti)}")

interno = df[df.sorgente.isin(espansi) & df.destinazione.isin(espansi)
             & (df.sorgente != df.destinazione)]
senza_out = len(espansi) - interno.sorgente.nunique()
print("\n--- rete finale ---")
print(f"Nodi:  {len(espansi)}")
print(f"Archi diretti: {len(interno)}")
print(f"Nodi senza raccomandazioni in uscita verso la rete: {senza_out}")
print(f"Out-degree massimo: {interno.sorgente.value_counts().max()} "
      f"(tetto della piattaforma: 50)")

interno.to_csv(DATA / "rete_finale.csv", index=False, header=False)
pd.Series(sorted(espansi)).to_csv(DATA / "nodi_finali.csv", index=False, header=False)
print("\nSalvati rete_finale.csv e nodi_finali.csv")
