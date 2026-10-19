"""PROVA - Esplora i metodi della classe Newsletter di substack_api
per capire quali informazioni sulle newsletter si possono ottenere"""
from substack_api import Newsletter

n = Newsletter("https://capitalwars.substack.com")

# Elenco dei metodi pubblici 
print("--- metodi disponibili ---")
print([m for m in dir(n) if not m.startswith("_")])

# Provo i metodi che sembrano utili stampo i primi 600 caratteri del risultato
for metodo in ["get_metadata", "get_authors", "get_posts"]:
    if hasattr(n, metodo):
        print(f"\n--- {metodo}() ---")
        try:
            r = getattr(n, metodo)()
            print(str(r)[:600])
        except Exception as e:
            print("errore:", e)