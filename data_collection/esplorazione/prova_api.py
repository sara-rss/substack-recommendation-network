import requests, time

HEAD = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}

test = ["https://capitalwars.substack.com",
        "https://chrishedges.substack.com",
        "https://georgesaunders.substack.com",
        "https://natesnewsletter.substack.com",
        "https://yourlocalepidemiologist.substack.com"]

for base in test:
    try:
        r = requests.get(base + "/api/v1/archive?limit=10", headers=HEAD, timeout=15)
        post = r.json()
        print(f"\n=== {base} ({len(post)} post) ===")
        if post:
            print("publication_id:", post[0].get("publication_id"))
        for p in post[:5]:
            titolo = p.get("title") or ""
            sotto = p.get("subtitle") or ""
            print(" -", titolo, "|", sotto[:60])
    except Exception as e:
        print(base, "errore:", e)
    time.sleep(1)