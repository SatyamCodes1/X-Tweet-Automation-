import os
from dotenv import load_dotenv

load_dotenv()

def env_bool(name: str, default: bool=False):
    v = os.getenv(name)
    if v is None: return default
    return str(v).strip().lower() in ("1","true","yes","y","on")

CONFIG = {
    "x": {
        "api_key": os.getenv("X_API_KEY"),
        "api_secret": os.getenv("X_API_SECRET"),
        "access_token": os.getenv("X_ACCESS_TOKEN"),
        "access_secret": os.getenv("X_ACCESS_SECRET"),
        "woeid": os.getenv("WOEID", "23424848"),
    },
    "llm": {
        "groq_api_key": os.getenv("GROQ_API_KEY"),
        "hf_token": os.getenv("HUGGINGFACEHUB_API_TOKEN"),
        "model": os.getenv("LLM_MODEL", "llama-3.1-8b-instant"),
        "temperature": float(os.getenv("LLM_TEMPERATURE", "0.8")),
        "max_tokens": int(os.getenv("LLM_MAX_TOKENS", "512")),
    },
    "news": {
        "country": os.getenv("DEFAULT_COUNTRY", "in"),
        "gnews_key": os.getenv("GNEWS_API_KEY"),
        "newsapi_key": os.getenv("NEWSAPI_KEY"),
        "gnews_limit": int(os.getenv("GNEWS_LIMIT", "20")),
        "newsapi_limit": int(os.getenv("NEWSAPI_LIMIT", "20")),
    },
    "posting": {
        "use_memes": env_bool("USE_MEMES", True),
        "meme_template": os.getenv("MEME_TEMPLATE", "assets/templates/meme1.jpg"),
        "trends_per_window": int(os.getenv("TRENDS_PER_WINDOW", "1")),
    },
    "hashtags": {
        "enabled": env_bool("HASHTAGS_ENABLED", True),
        "max_count": int(os.getenv("HASHTAGS_MAX", "2")),
        "disable_on_sensitive": env_bool("DISABLE_HASHTAGS_ON_SENSITIVE", True),
    },
    "limits": {
        "daily": int(os.getenv("DAILY_TWEET_LIMIT", "15")),
        "monthly": int(os.getenv("MONTHLY_TWEET_LIMIT", "450")),
    },
    "safety": {
        "avoid_sensitive_humor": env_bool("AVOID_SENSITIVE_HUMOR", True),
        "critique_authorities": env_bool("CRITIQUE_AUTHORITIES", True),  # respectful accountability
    },
    "logging": {
        "file": os.getenv("LOG_FILE", "bot.log"),
    },
    "db": {
        "path": os.getenv("DB_PATH", "bot.sqlite3")
    },
    "testing": {
        "test_mode": env_bool("TEST_MODE", False),
    }
}
