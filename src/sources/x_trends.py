import tweepy
from ..config import CONFIG

def get_trends():
    auth = tweepy.OAuth1UserHandler(
        CONFIG["x"]["api_key"],
        CONFIG["x"]["api_secret"],
        CONFIG["x"]["access_token"],
        CONFIG["x"]["access_secret"]
    )
    api = tweepy.API(auth)
    woeid = int(CONFIG["x"]["woeid"])
    trends = api.get_place_trends(id=woeid)  # list with [0]["trends"]
    return trends

def select_topics(trends_json, limit=2):
    items = trends_json[0]["trends"]
    items = sorted(items, key=lambda t: (t.get("tweet_volume") or 0), reverse=True)
    out = []
    for t in items:
        name = t.get("name","" )
        if not name: 
            continue
        if len(out) >= limit: 
            break
        lname = name.lower()
        if any(bad in lname for bad in ("nsfw", "porn")):
            continue
        out.append(name)
    return out
