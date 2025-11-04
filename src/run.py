import sys
from .orchestrator import run_trend_window, run_news_post_batch, cache_news_batch

if __name__ == "__main__":
    trigger = None
    if len(sys.argv) > 1:
        for arg in sys.argv:
            if arg.startswith("TRIGGER="):
                trigger = arg.split("=")[1]

    if trigger == "trend_window":
        print("✅ Trigger: trend_window")
        run_trend_window()
    elif trigger == "cache_news":
        print("✅ Trigger: cache_news")
        cache_news_batch()
    elif trigger == "news_batch":
        print("✅ Trigger: news_batch")
        # news per run defaults to 1; can override via env NEWS_BATCH_COUNT if you want
        run_news_post_batch(count=1)
    else:
        print("⚠️ No valid TRIGGER provided. Use:")
        print("   python -m src.run TRIGGER=trend_window")
        print("   python -m src.run TRIGGER=cache_news")
        print("   python -m src.run TRIGGER=news_batch")
