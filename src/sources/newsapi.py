import requests
from ..config import CONFIG

def fetch_newsapi(n=20, country=None):
    key = CONFIG["news"]["newsapi_key"]
    if not key:
        return []
    country = country or CONFIG["news"]["country"]
    url = f"https://newsapi.org/v2/top-headlines?country={country}&pageSize={n}&apiKey={key}"
    r = requests.get(url, timeout=20)
    r.raise_for_status()
    j = r.json()
    arts = []
    for a in j.get("articles", []):
        arts.append((a.get("title",""), a.get("description",""), a.get("url","")))
    return arts[:n]
