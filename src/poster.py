# src/poster.py

import tweepy
from .config import CONFIG
from .utils import get_logger

log = get_logger()


def _get_api_v1():
    """Return Tweepy API v1.1 client (OAuth 1.0a User Context)."""
    auth = tweepy.OAuth1UserHandler(
        CONFIG["x"]["api_key"],
        CONFIG["x"]["api_secret"],
        CONFIG["x"]["access_token"],
        CONFIG["x"]["access_secret"]
    )
    return tweepy.API(auth)


def _get_api_v2():
    """Return Tweepy API v2 client (OAuth 2.0 User Context)."""
    return tweepy.Client(
        consumer_key=CONFIG["x"]["api_key"],
        consumer_secret=CONFIG["x"]["api_secret"],
        access_token=CONFIG["x"]["access_token"],
        access_token_secret=CONFIG["x"]["access_secret"]
    )


def post_text(text: str):
    """
    ✅ Text-only Tweet using API v2 (Free + Works on Essential Access).
    """
    try:
        api = _get_api_v2()
        response = api.create_tweet(text=text)
        tweet_id = response.data.get("id")
        log.info(f"✅ Tweet posted → ID: {tweet_id}")
        return tweet_id
    except Exception as e:
        log.error(f"❌ Failed to post tweet: {e}")
        return None


def post_text_with_media(text: str, image_path: str):
    """
    ⚠ Media Tweet using API v1.1 — Requires Elevated Access.
    ✅ If USE_MEMES=false, this function is never used.
    """
    try:
        api = _get_api_v1()
        media = api.media_upload(image_path)
        res = api.update_status(status=text, media_ids=[media.media_id_string])
        log.info(f"✅ Tweet with image posted → ID: {res.id}")
        return res.id
    except tweepy.Forbidden:
        log.error(
            "❌ 403 Error: Your Twitter app doesn't allow media uploads.\n"
            "➡ Fix: Disable USE_MEMES or request Elevated API access."
        )
        return None
    except Exception as e:
        log.error(f"❌ Media tweet failed: {e}")
        return None
