from datetime import datetime, timedelta, timezone
import feedparser

from .config import CONFIG
from .db import connect, seen_hash, mark_posted, cache_item, select_uncached
from .utils import mkhash, clean_topic, get_logger, is_sensitive
from .llm import make_tweet, translate_to_hindi
from .meme import make_meme
from .poster import post_text, post_text_with_media

# ✅ You missed these ↓
from .sources.gnews import fetch_gnews
from .sources.newsapi import fetch_newsapi

log = get_logger()


# ------------------ (1) Posting Limits ------------------
def _iso_bounds_utc():
    now = datetime.now(timezone.utc)
    start_day = datetime(now.year, now.month, now.day, tzinfo=timezone.utc)
    next_day = start_day + timedelta(days=1)
    start_month = datetime(now.year, now.month, 1, tzinfo=timezone.utc)
    next_month = (
        datetime(now.year + 1, 1, tzinfo=timezone.utc)
        if now.month == 12
        else datetime(now.year, now.month + 1, 1, tzinfo=timezone.utc)
    )
    return start_day.isoformat(), next_day.isoformat(), start_month.isoformat(), next_month.isoformat()


def _counts(con):
    sd, nd, sm, nm = _iso_bounds_utc()
    daily = con.execute("SELECT COUNT(*) FROM posts WHERE posted_at >= ? AND posted_at < ?", (sd, nd)).fetchone()[0]
    monthly = con.execute("SELECT COUNT(*) FROM posts WHERE posted_at >= ? AND posted_at < ?", (sm, nm)).fetchone()[0]
    return daily, monthly


def _allowed_to_post(con):
    daily, monthly = _counts(con)
    if daily >= CONFIG["limits"]["daily"]:
        return False, f"⚠️ Daily limit reached ({daily}/{CONFIG['limits']['daily']})"
    if monthly >= CONFIG["limits"]["monthly"]:
        return False, f"⚠️ Monthly limit reached ({monthly}/{CONFIG['limits']['monthly']})"
    return True, f"✅ Posting allowed (daily={daily}, monthly={monthly})"


# ------------------ (2) Single Tweet Posting ------------------
def post_one_tweet(text_hindi: str, source: str, url: str = None, use_meme: bool = True, con=None):
    """✅ Post only ONE tweet. If it fails → stop, no retry."""
    h = mkhash(text_hindi, url or "", source)

    # Avoid duplicates
    if con and seen_hash(con, h):
        log.info(f"⏩ डुप्लिकेट स्किप ({source}): {text_hindi[:50]}…")
        return False

    allowed, reason = _allowed_to_post(con)
    if not allowed:
        log.warning(f"🚫 {reason} — skipping this tweet.")
        return False

    log.info(f"✅ {reason} — posting now…")

    try:
        if CONFIG["testing"]["test_mode"]:
            log.info(f"[TEST_MODE] ❌ Not posting to X — {text_hindi}")
            tweet_id, media_hash = None, None
        else:
            if use_meme:
                path, media_hash = make_meme(text_hindi)
                tweet_id = post_text_with_media(text_hindi, path)
            else:
                media_hash = None
                tweet_id = post_text(text_hindi)

        if not tweet_id:
            log.error("❌ Posting failed — not retrying this run.")
            return False

        if con:
            mark_posted(con, h, text_hindi, source, url or "", media_hash, tweet_id)

        return True

    except Exception as e:
        log.error(f"❌ Fatal Error: {e} — Stopping.")
        return False


# ------------------ (3) Hindi News Posting (Batch = 1 Tweet) ------------------
def run_news_post_batch(count=1):
    """✅ Posts exactly ONE tweet (count=1). Stops after first success OR fail."""
    log.info(f"📢 {count} हिंदी न्यूज़ पोस्ट करने की कोशिश…")
    con = connect(CONFIG["db"]["path"])
    rows = select_uncached(con, limit=50)

    if not rows:
        log.warning("⛔ कोई नई खबर उपलब्ध नहीं — पहले cache_news चलाओ")
        return

    posted = 0
    for h, title, desc, url, source in rows:
        if posted >= count:
            break

        raw = f"{title} — {desc}" if desc else title or ""
        hindi_tweet = make_tweet(raw, mode="funny", add_hashtags_from=raw)

        success = post_one_tweet(hindi_tweet, source=source, url=url, use_meme=False, con=con)
        posted += 1
        break  # ✅ Stop after first tweet attempt (success or fail)

    log.info(f"✅ {posted} ट्वीट पोस्ट करने का प्रयास समाप्त ✅")


# ------------------ (4) Optional: Cache News ------------------
def cache_news_batch():
    log.info("🗞 समाचार सेव कर रहे हैं…")
    con = connect(CONFIG["db"]["path"])

    try:
        items = fetch_gnews(CONFIG["news"]["gnews_limit"])
        src = "gnews"
    except:
        if CONFIG["news"]["newsapi_key"]:
            items = fetch_newsapi(CONFIG["news"]["newsapi_limit"])
            src = "newsapi"
        else:
            log.error("❌ No news source available.")
            return

    for title, desc, url in items:
        h = mkhash(title or "", desc or "", url or "")
        cache_item(con, h, title, desc, url, src)

    log.info("✅ News cached in database.")


# ------------------ (5) Trend Posting (Google RSS) ------------------
def run_trend_window():
    log.info("📡 ट्रेंडिंग RSS (हिंदी) लाया जा रहा है…")
    con = connect(CONFIG["db"]["path"])

    try:
        feed = feedparser.parse("https://news.google.com/rss?hl=hi-IN&gl=IN&ceid=IN:hi")
        topics = [clean_topic(entry.title) for entry in feed.entries if clean_topic(entry.title)]
        topics = topics[:CONFIG["posting"]["trends_per_window"]]
        log.info(f"🔥 Topics: {topics}")
    except Exception as e:
        log.error(f"❌ RSS Error: {e}")
        return

    for topic in topics:
        text_hi = translate_to_hindi(topic)
        sensitive = is_sensitive(text_hi)

        if sensitive and CONFIG["safety"]["avoid_sensitive_humor"]:
            mode = "accountability"
            use_meme = False
        else:
            mode = "funny"
            use_meme = CONFIG["posting"]["use_memes"]

        tweet = make_tweet(text_hi, mode=mode, add_hashtags_from=text_hi)
        post_one_tweet(tweet, source="trend_hi", use_meme=use_meme, con=con)
        break  # ✅ Only one trend tweet per run
