import sqlite3
from datetime import datetime

SCHEMA = """
CREATE TABLE IF NOT EXISTS posts (
  id INTEGER PRIMARY KEY,
  hash TEXT UNIQUE,
  text TEXT,
  source TEXT,
  url TEXT,
  media_hash TEXT,
  posted_at TEXT,
  external_id TEXT
);

CREATE TABLE IF NOT EXISTS cache_items (
  id INTEGER PRIMARY KEY,
  hash TEXT UNIQUE,
  title TEXT,
  desc TEXT,
  url TEXT,
  source TEXT,
  created_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_posts_hash ON posts(hash);
CREATE INDEX IF NOT EXISTS idx_cache_hash ON cache_items(hash);
"""

def connect(db_path: str):
    con = sqlite3.connect(db_path)
    con.execute("PRAGMA journal_mode=WAL;")
    con.executescript(SCHEMA)
    return con

def seen_hash(con, h: str) -> bool:
    cur = con.execute("SELECT 1 FROM posts WHERE hash=?", (h,))
    return cur.fetchone() is not None

def mark_posted(con, h: str, text: str, source: str, url: str, media_hash: str, external_id: str=None):
    con.execute(
        "INSERT OR IGNORE INTO posts(hash, text, source, url, media_hash, posted_at, external_id) VALUES(?,?,?,?,?,?,?)",
        (h, text, source, url, media_hash, datetime.utcnow().isoformat(), external_id)
    )
    con.commit()

def cache_item(con, h: str, title: str, desc: str, url: str, source: str):
    con.execute(
        "INSERT OR IGNORE INTO cache_items(hash, title, desc, url, source, created_at) VALUES(?,?,?,?,?,?)",
        (h, title, desc, url, source, datetime.utcnow().isoformat())
    )
    con.commit()

def select_uncached(con, limit=50):
    cur = con.execute("SELECT hash, title, desc, url, source FROM cache_items ORDER BY id DESC LIMIT ?", (limit,))
    return cur.fetchall()
