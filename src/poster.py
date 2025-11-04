import os
import tweepy
from .config import CONFIG

TEST_MODE = os.getenv("TEST_MODE", "false").lower() == "true"

def get_api():
    auth = tweepy.OAuth1UserHandler(
        CONFIG["x"]["api_key"],
        CONFIG["x"]["api_secret"],
        CONFIG["x"]["access_token"],
        CONFIG["x"]["access_secret"]
    )
    return tweepy.API(auth)

def post_text(text: str):
    if TEST_MODE:
        print("[TEST_MODE ON] Would post tweet:", text)
        return "test-id"
    api = get_api()
    res = api.update_status(status=text)
    return str(res.id)

def post_text_with_media(text: str, media_path: str):
    if TEST_MODE:
        print(f"[TEST_MODE ON] Would post meme tweet: {text}\nWith image: {media_path}")
        return "test-id"
    api = get_api()
    media = api.media_upload(media_path)
    res = api.update_status(status=text, media_ids=[media.media_id_string])
    return str(res.id)
