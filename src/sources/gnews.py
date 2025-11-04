import requests
from ..config import CONFIG

def fetch_gnews(n=20, country=None):
    key = CONFIG["news"]["gnews_key"]
    country = country or CONFIG["news"]["country"]
    url = f"https://gnews.io/api/v4/top-headlines?country={country}&max={n}&apikey={key}&lang=en"
    r = requests.get(url, timeout=20)
    r.raise_for_status()
    data = r.json()
    articles = []
    for a in data.get("articles", []):
        title = a.get("title") or ""
        desc = a.get("description") or ""
        link = a.get("url") or ""
        articles.append((title, desc, link))
    return articles[:n]
