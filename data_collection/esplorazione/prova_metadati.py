from substack_api import Newsletter

n = Newsletter("https://capitalwars.substack.com")

print("--- metodi disponibili ---")
print([m for m in dir(n) if not m.startswith("_")])

for metodo in ["get_metadata", "get_authors", "get_posts"]:
    if hasattr(n, metodo):
        print(f"\n--- {metodo}() ---")
        try:
            r = getattr(n, metodo)()
            print(str(r)[:600])
        except Exception as e:
            print("errore:", e)