import re
import logging
import hashlib
import textwrap
import unicodedata
from typing import List

_LOGGER = None

def get_logger():
    global _LOGGER
    if _LOGGER:
        return _LOGGER
    logger = logging.getLogger("x-funny-news-bot")
    if not logger.handlers:
        handler = logging.StreamHandler()
        fmt = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
        handler.setFormatter(fmt)
        logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    _LOGGER = logger
    return logger

def mkhash(*parts: str) -> str:
    h = hashlib.sha1("||".join([p or "" for p in parts]).encode("utf-8")).hexdigest()
    return h

def clean_topic(s: str) -> str:
    if not s:
        return ""
    s = s.strip()
    # remove duplicate spaces & weird unicode spaces
    s = " ".join(s.split())
    return s

def wrap_for_meme(text: str, width: int = 22) -> str:
    return textwrap.fill(text or "", width=width)

# --- Detox: replace common slurs/abuse with placeholder ---
_SLURS = [
    r"\bबेवकूफ\b", r"\bहरामी\b", r"\bकमीना\b", r"\bचुतिया\b", r"\bभोसडीके\b",
    r"\basshole\b", r"\bbastard\b", r"\bidiot\b", r"\bmoron\b"
]
def detox(text: str) -> str:
    if not text:
        return text
    out = text
    for pat in _SLURS:
        out = re.sub(pat, "〔हटाया गया〕", out, flags=re.IGNORECASE)
    return out

# --- Sensitivity detection (Hindi + English keywords) ---
_SENSITIVE_PATTERNS = [
    r"\bमौत\b|\bमारा गया\b|\bमारे गए\b|\bदम तोड़\b|\bशव\b|\bअंतिम\sसंस्कार\b",
    r"\bहादसा\b|\bदुर्घटना\b|\bट्रेन\b|\bबस\b|\bटकरा\b|\bरेल\b",
    r"\bबाढ़\b|\bबाढ़\b|\bभूकंप\b|\bभूस्खलन\b|\bतूफान\b|\bcyclone\b|\bflood\b|\bearthquake\b",
    r"\bऑक्सीजन\b|\boxygen\b|\bICU\b|\bhospital\b|\bअस्पताल\b",
    r"\brape\b|\bबलात्कार\b|\bहत्या\b|\bmurder\b|\blynch\b|\bलिंच\b",
    r"\bfire\b|\bआग\b|\bblast\b|\bविस्फोट\b",
    r"\bbridge\b|\bपुल\b|\bcollapse\b|\bगिर\b",
    r"\bnegligence\b|\bलापरवाही\b|\bcorruption\b|\bभ्रष्टाचार\b",
    r"\bwar\b|\bयुद्ध\b|\bदंगा\b|\briot\b",
]
def is_sensitive(text: str) -> bool:
    if not text:
        return False
    t = unicodedata.normalize("NFKC", text)
    for pat in _SENSITIVE_PATTERNS:
        if re.search(pat, t, flags=re.IGNORECASE):
            return True
    return False

# --- Hashtags in Hindi (no English spam) ---
_HINDI_STOP = set([
    "है","और","का","की","के","से","तो","था","थी","पर","में","को","ने","हो","हैं",
    "ये","यह","वो","या","भी","सब","क्यों","कब","बहुत","ज्यादा","फिर","अब","पर",
    "लिए","करे","किया","कर","होना","रहा","रही","रहे","एक","दो","तीन"
])
def _clean_token(tok: str) -> str:
    tok = tok.strip().strip(".,:;!?()[]{}\"'`।…–-")
    tok = re.sub(r"[^0-9\u0900-\u097F]+", "", tok)  # keep Devanagari + digits
    return tok

def hashtagify(text: str, max_count: int = 2) -> str:
    if not text:
        return ""
    words = [_clean_token(w) for w in text.split()]
    words = [w for w in words if w and (w not in _HINDI_STOP) and len(w) >= 3]
    # uniq, keep order
    seen = set()
    tags: List[str] = []
    for w in words:
        if w in seen:
            continue
        seen.add(w)
        tags.append("#" + w)
        if len(tags) >= max_count:
            break
    return (" " + " ".join(tags)) if tags else ""

def safe_tweet(text: str) -> str:
    if not text:
        return ""
    # Trim hard to 280 chars (X limit); keep link if present on a new line
    t = text.strip()
    if len(t) <= 280:
        return t
    # Try to preserve last line if it's a link
    lines = t.splitlines()
    if lines and ("http://" in lines[-1] or "https://" in lines[-1]):
        base = "\n".join(lines[:-1])
        base = base[: max(0, 280 - (len(lines[-1]) + 1))].rstrip()
        return (base + "\n" + lines[-1]).strip()[:280]
    return t[:280].rstrip()
