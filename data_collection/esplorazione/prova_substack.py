"""PROVA - Verifica che get_recommendations() funzioni sui 15 seed
e stampa quante raccomandazioni ha ciascuno"""
from substack_api import Newsletter

seed = [
    # letteratura
    "https://georgesaunders.substack.com",
    "https://footnotesandtangents.substack.com",
    "https://pandorasykes.substack.com",
    # politica
    "https://greenwald.substack.com",
    "https://samf.substack.com",
    "https://chrishedges.substack.com",
    # tecnologia
    "https://natesnewsletter.substack.com",
    "https://newsletter.pragmaticengineer.com",
    "https://damnang2.substack.com",
    # finanza
    "https://michaeljburry.substack.com",
    "https://capitalwars.substack.com",
    "https://charliepgarcia.substack.com",
    # scienza e salute
    "https://yourlocalepidemiologist.substack.com",
    "https://theskepticalcardiologist.substack.com",
    "https://theunbiasedscipod.substack.com",
]

for url in seed:
    try:
        print(url, "->", len(Newsletter(url).get_recommendations()))
    except Exception as e:
        print(url, "ERRORE", e)