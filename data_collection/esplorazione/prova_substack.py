from substack_api import Newsletter

seed = [
    "https://georgesaunders.substack.com",
    "https://footnotesandtangents.substack.com",
    "https://pandorasykes.substack.com", #fine letteratura
    "https://greenwald.substack.com",
    "https://samf.substack.com",
    "https://chrishedges.substack.com", #politica
    "https://natesnewsletter.substack.com",
    "https://newsletter.pragmaticengineer.com",
    "https://damnang2.substack.com", #tecnologia
    "https://michaeljburry.substack.com",
    "https://capitalwars.substack.com",
    "https://charliepgarcia.substack.com", #finance
    "https://yourlocalepidemiologist.substack.com",
    "https://theskepticalcardiologist.substack.com",
    "https://theunbiasedscipod.substack.com", #science
]

for url in seed:
    try:
        print(url, "->", len(Newsletter(url).get_recommendations()))
    except Exception as e:
        print(url, "ERRORE", e)