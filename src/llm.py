# ✅ src/llm.py — Gen-Z Hinglish Multi-line Tweet Generator (Improved + Meaningful)
# Output style:
# "लाइन 1
#  लाइन 2
#  लाइन 3
#  लाइन 4 (optional)"
#
# - Always 3–4 lines with CONCRETE comparisons
# - 1–2 emojis placed strategically
# - STRONG contrast between government action vs ground reality
# - No hashtags, @mentions, or links INSIDE body
# - ≤ 280 chars total
# - Keeps translation, detox, sensitivity logic intact


from .config import CONFIG
from .utils import safe_tweet, hashtagify, detox, is_sensitive
import re
from groq import Groq


# ---------------------- ENHANCED STYLE PROMPTS (Concrete + Meaningful) -------------------------


FUNNY_STYLE_HI = (
    "तुम एक SHARP Gen-Z न्यूज़ कॉमेंटेटर हो जो खबरों पर तीखे, concrete अवलोकन और relatable सच्चाई के साथ मीम-वाइब में लिखता है। "
    "\n\n🎯 MOST IMPORTANT - STRUCTURE (MUST FOLLOW):\n"
    "Line 1: CONCRETE OBSERVATION - एक specific, measurable reality state करो (e.g., 'चांद पर मिशन और धरती पर गड्ढे')\n"
    "Line 2: CONTRAST - Government action vs ground reality (use 'X कर रहा है, Y सो रहा है' pattern) + emoji\n"
    "Line 3: CONSEQUENCE/IRONY - Direct impact या philosophical observation (e.g., 'Budget से याद आया')\n"
    "Line 4: CLOSING DEMAND/SARCASM - Sharp wrap-up (optional but powerful)\n"
    "\n\n📋 EXACT EXAMPLES TO MATCH:\n"
    "Example 1:\n"
    "चांद पर मिशन और धरती पर गड्ढे\n"
    "ISRO launch कर रहा है, नगर निगम सो रहा है 😭\n"
    "Budget से याद आया –\n"
    "पहले सड़क ठीक कर दो फिर रॉकेट उड़ाना!\n"
    "\n"
    "Example 2:\n"
    "हवा में जहर, फेफड़ों में धुआं\n"
    "सरकार बोले mask लगा लो, pollution कंट्रोल करने की जिम्मेदारी भूल गए 😤\n"
    "Delhi AQI 500+ और हम सब मास्क carnival चला रहे हैं\n"
    "क्या ये development है या सिस्टम failure?\n"
    "\n"
    "भाषा: Hindi (Devanagari) + natural English words (ISRO, launch, budget, mission, pollution, development, AQI, system, action, reality)\n"
    "Emoji: 😭😤😅🤡💀 - सिर्फ 1-2, line 2 या 3 में\n"
    "कोई hashtag, @mention, या link नहीं\n"
    "हर लाइन में concrete detail + sarcasm + relatability होनी चाहिए\n"
)


SERIOUS_STYLE_HI = (
    "तुम एक calm but SHARP Gen-Z न्यूज़ राइटर हो जो facts देता है, बिना drama के। "
    "\n\n📋 STRUCTURE:\n"
    "Line 1: Main fact/concrete observation\n"
    "Line 2: What government claims vs what's actually happening\n"
    "Line 3: Real impact (numbers, data, या ground reality)\n"
    "Line 4: Closing observation (thought-provoking)\n"
    "\nभाषा: Hindi + few English words (system, data, reality, report, action, impact)\n"
    "Emoji: 0-1 only\n"
    "Tone: Sharp observations, no drama\n"
)


ACCOUNTABILITY_STYLE_HI = (
    "तुम एक DIRECT जवाबदेही-focused पत्रकार हो जो system failures को concrete examples से उजागर करता है। "
    "\n\n📋 STRUCTURE:\n"
    "Line 1: Concrete problem/failure (specific example, not generic)\n"
    "Line 2: Government/authority claims vs reality (CONTRAST)\n"
    "Line 3: Direct question for accountability (किसकी जिम्मेदारी?)\n"
    "Line 4: People ka sach (what common people suffer)\n"
    "\nभाषा: Hindi + English (accountability, system, failure, reality, action, responsibility)\n"
    "Emoji: 1 max\n"
    "Tone: Sharp questions, no drama, direct accountability\n"
)


TRANSLATE_TO_HINDI_PROMPT = (
    "इस वाक्य को simple, CONCRETE Hindi में बदलो (Gen-Z टच चलेगा)। "
    "Natural English/tech words use कर सकते हो: ISRO, budget, system, pollution, mission, launch, development, AQI, action, reality, impact। "
    "Over-dramatic नहीं, crisp रखो। Numbers English: 1, 2, 3। "
    "केवल अनुवाद दो, कुछ और नहीं।\n\n"
    "वाक्य:\n"
)


# Allowed Gen-Z English words
GEN_Z_WORDS = [
    "ISRO","launch","budget","mission","pollution","development","AQI","system","action","reality","impact",
    "bro","cringe","scene","vibe","mood","sarcasm","drama","fail","win","level","report",
    "news","shock","alert","tweet","share","data","hack","app","AI","update","accountability",
    "responsibility","concrete","observation","contrast","claim","vs","orbit","rocket","train","road"
]


# ---------------------- HINDI DETECTION -------------------------
def contains_hindi(text: str) -> bool:
    if not text:
        return False
    return bool(re.search(r'[\u0900-\u097F]', text))


def get_hindi_percentage(text: str) -> float:
    if not text:
        return 0.0
    text_clean = re.sub(r'[\s.,;:!?\n\r\-0-9"\'\(\):]', '', text)
    if not text_clean:
        return 0.0
    hindi_chars = len(re.findall(r'[\u0900-\u097F]', text_clean))
    total_chars = len(text_clean)
    return (hindi_chars / total_chars * 100) if total_chars > 0 else 0.0


def normalize_numbers(text: str) -> str:
    hindi_to_english = {'०':'0','१':'1','२':'2','३':'3','४':'4','५':'5','६':'6','७':'7','८':'8','९':'9'}
    for hi, en in hindi_to_english.items():
        text = text.replace(hi, en)
    return text


# ---------------------- GROQ CALLER -------------------------
def _groq_client():
    return Groq(api_key=CONFIG["llm"]["groq_api_key"])


def call_groq(prompt: str, system: str = None, temperature: float = 0.85, max_tokens: int = 300) -> str:
    try:
        client = _groq_client()
        msgs = []
        if system:
            msgs.append({"role": "system", "content": system})
        msgs.append({"role": "user", "content": prompt})
        
        out = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=msgs,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        return normalize_numbers(out.choices[0].message.content.strip())
    except Exception as e:
        print(f"❌ Groq Error: {e}")
        return ""


# ---------------------- TRANSLATION -------------------------
def translate_to_hindi(text: str) -> str:
    if not text or not text.strip():
        return ""
    if get_hindi_percentage(text) > 80:
        return normalize_numbers(text.strip())

    print(f"🔄 Translating to Hinglish: {text[:60]}...")
    system = (
        "You are a Gen-Z Hindi translator. "
        "Write MOSTLY in Hindi (Devanagari). "
        "Use natural English words only when needed: " + ", ".join(GEN_Z_WORDS) + ". "
        "Use English numerals (1, 2, 3). One concise line only."
    )
    prompt = f"{TRANSLATE_TO_HINDI_PROMPT}{text}"
    result = call_groq(prompt, system, temperature=0.4, max_tokens=120)
    if result and contains_hindi(result):
        pct = get_hindi_percentage(result)
        if pct >= 50:
            print(f"✅ Translation success ({pct:.0f}% Hindi): {result[:60]}...")
            return result.strip()
        print(f"⚠ Low Hindi percentage: {pct:.0f}%")
    print("❌ Translation failed")
    return text.strip()


# ---------------------- UTILITIES FOR MULTI-LINE -------------------------
def _clean_lines(text: str) -> str:
    lines = [ln.strip() for ln in text.replace("\r", "").split("\n")]
    lines = [ln for ln in lines if ln]
    return "\n".join(lines)


def _limit_words_per_line(text: str, max_words: int = 18) -> str:
    lines = text.split("\n")
    clipped = []
    for ln in lines:
        words = ln.split()
        if len(words) > max_words:
            ln = " ".join(words[:max_words])
        clipped.append(ln.strip())
    return "\n".join([l for l in clipped if l])


def _strip_forbidden(text: str) -> str:
    # Remove hashtags, mentions, links inside body
    lines = text.split("\n")
    out = []
    for ln in lines:
        ln = re.sub(r"(#[^\s]+|@[^\s]+|https?://\S+)", "", ln).strip()
        out.append(ln)
    text = "\n".join(out)
    # Collapse multiple spaces
    text = re.sub(r"[ \t]{2,}", " ", text)
    return _clean_lines(text)


def _emoji_count(s: str) -> int:
    return len(re.findall(r"[\U0001F300-\U0001FAFF]", s))


def _limit_emojis(text: str, max_emoji: int = 2) -> str:
    while _emoji_count(text) > max_emoji:
        text = re.sub(r"([\U0001F300-\U0001FAFF])", "", text, count=1)
    return text


def _enforce_line_count(text: str, min_lines: int = 3, max_lines: int = 4) -> str:
    lines = [ln for ln in text.split("\n") if ln.strip()]
    if len(lines) > max_lines:
        lines = lines[:max_lines]
    return "\n".join(lines)


# ---------------------- IMPROVED MULTI-LINE POST GENERATION -------------------------
def generate_multiline_post(core: str, mode: str) -> str:
    """
    Generate 3–4 MEANINGFUL lines with concrete contrasts, strong observations, and sarcasm.
    Focus on: Concrete reality → Government action vs what's needed → Sharp observation
    """
    style_map = {
        "funny": FUNNY_STYLE_HI,
        "serious": SERIOUS_STYLE_HI,
        "accountability": ACCOUNTABILITY_STYLE_HI
    }
    style = style_map.get(mode, FUNNY_STYLE_HI)

    system = (
        "You are a SAVAGE Gen-Z Hindi tweet writer who writes MEANINGFUL, concrete news commentary with strong observations.\n"
        "\n🎯 YOUR MISSION: Write exactly 3-4 lines that are CONCRETE + FUNNY + MEANINGFUL (not generic).\n"
        "\n📋 MANDATORY STRUCTURE:\n"
        "Line 1: CONCRETE OBSERVATION or COMPARISON (e.g., 'चांद पर मिशन और धरती पर गड्ढे' or 'हवा में जहर, फेफड़ों में धुआं')\n"
        "Line 2: CONTRAST (X कर रहा है, Y सो रहा है OR Government claims vs reality) + emoji (😭😤😅🤡💀)\n"
        "Line 3: CONSEQUENCE/IRONY with CONCRETE detail (number, example, या real-world impact)\n"
        "Line 4: SHARP CLOSING (demand, sarcastic question, या powerful statement)\n"
        "\n✨ EXAMPLES TO MATCH (VERY IMPORTANT):\n"
        "Example 1:\n"
        "चांद पर मिशन और धरती पर गड्ढे\n"
        "ISRO launch कर रहा है, नगर निगम सो रहा है 😭\n"
        "Budget से याद आया –\n"
        "पहले सड़क ठीक कर दो फिर रॉकेट उड़ाना!\n"
        "\n"
        "Example 2:\n"
        "हवा में जहर, फेफड़ों में धुआं\n"
        "सरकार बोले mask लगा लो, pollution कंट्रोल करने की जिम्मेदारी भूल गए 😤\n"
        "Delhi AQI 500+ और हम सब मास्क carnival चला रहे हैं\n"
        "क्या ये development है या सिस्टम failure?\n"
        "\n🚫 HARD RULES:\n"
        "- CONCRETE: हमेशा specific numbers, examples, या ground reality दो (generic नहीं)\n"
        "- CONTRAST: Line 2 में X vs Y का clear pattern रखो\n"
        "- LANGUAGE: Hindi + few English words (ISRO, budget, mission, system, pollution, AQI, launch, action, reality)\n"
        "- NO hashtags, NO @mentions, NO links\n"
        "- EMOJI: Exactly 1-2, Line 2 या 3 में\n"
        "- 3-4 lines only, NO extra commentary\n"
        "- Each line meaningful, sarcastic, relatable, and CONCRETE\n"
        "\n🎭 TONE: Savage, witty, sharp, philosophical sarcasm, ground reality + government failure contrast"
    )

    user_prompt = (
        f"{style}\n\n"
        f"📰 NEWS/TOPIC:\n{core}\n\n"
        f"अब इस topic पर उपर दिए गए EXAMPLES की तरह 3-4 CONCRETE, MEANINGFUL lines लिखो।\n"
        f"RULES:\n"
        f"• Line 1: Concrete observation (specific, measurable)\n"
        f"• Line 2: Clear X vs Y contrast + emoji\n"
        f"• Line 3: Real consequence or ironic detail\n"
        f"• Line 4: Sharp closing demand or sarcasm\n"
        f"सिर्फ 3-4 lines लौटाओ, कुछ और नहीं। MEANINGFUL और CONCRETE होना चाहिए।"
    )

    out = call_groq(user_prompt, system, temperature=0.90, max_tokens=270)
    if not out:
        return core

    text = _clean_lines(out)
    
    # If single paragraph, intelligently split
    if "\n" not in text and len(text) > 100:
        parts = re.split(r'[।!\?]\s+', text)
        parts = [p.strip() for p in parts if p.strip()]
        if len(parts) >= 3:
            text = "\n".join(parts[:4])

    # Sanitize
    text = _strip_forbidden(text)
    text = _limit_words_per_line(text, max_words=18)
    text = _enforce_line_count(text, min_lines=3, max_lines=4)
    text = _limit_emojis(text, max_emoji=2)
    text = normalize_numbers(detox(text))
    return text


# ---------------------- MAIN TWEET FUNCTION -------------------------
def make_tweet(
    topic: str,
    link: str = None,
    mode: str = "funny",
    add_hashtags_from: str = None
) -> str:
    """Generate a meaningful multi-line Gen-Z Hinglish tweet (3–4 lines)."""

    if not topic or not topic.strip():
        return "⚠ अरे भाई, विषय तो दे दो! 😅"

    print(f"\n{'='*60}")
    print(f"🐦 Making tweet for: {topic[:60]}...")

    # 1) Translate topic to Hindi
    core = translate_to_hindi(topic)
    if not contains_hindi(core):
        print("⚠ Translation weak, using original as core")
        core = topic.strip()

    # 2) Sensitivity check
    sensitive = is_sensitive(core)
    if sensitive and mode == "funny":
        mode = "accountability" if CONFIG["safety"].get("critique_authorities") else "serious"

    # 3) Generate body
    body = generate_multiline_post(core, mode)

    # 4) Wrap in quotes
    body_wrapped = body.strip()
    if not body_wrapped.startswith(("\"", """)):
        body_wrapped = f"\"{body_wrapped}"
    if not body_wrapped.endswith(("\"", """)):
        body_wrapped = f"{body_wrapped}\""
    body_wrapped = body_wrapped.replace(""", "\"").replace(""", "\"")

    # 5) Append link
    link_part = f"\n🔗 {link}" if link else ""
    final_text = f"{body_wrapped}{link_part}"

    # 6) Optional hashtags
    tags = ""
    if add_hashtags_from and not sensitive:
        print(f"🔖 Generating hashtags from: {add_hashtags_from[:50]}...")
        hindi_src = translate_to_hindi(add_hashtags_from)
        if contains_hindi(hindi_src):
            tags = hashtagify(
                hindi_src,
                max_count=CONFIG.get("hashtags", {}).get("max_count", 3)
            )
            if tags:
                print(f"✅ Hashtags: {tags}")

    # 7) Final cleanups
    final_tweet = (final_text + " " + tags).strip()
    final_tweet = normalize_numbers(safe_tweet(final_tweet))

    # 8) Metrics
    hindi_pct = get_hindi_percentage(final_tweet)
    preview = final_tweet.replace("\n", "\\n")
    print(f"✅ Final tweet ({len(final_tweet)} chars, {hindi_pct:.0f}% Hindi, Meaningful Gen-Z ✨):")
    print(f"   {preview[:250]}...")
    print(f"{'='*60}\n")

    return final_tweet


# ---------------------- TESTING -------------------------
def test_translation():
    """Quick translation tests"""
    tests = [
        "India launches Chandrayaan while potholes damage roads",
        "Delhi pollution reaches hazardous levels",
        "Government announces bullet train while local trains overcrowded",
        "Paper leak scandal in Rajasthan triggers protests",
        "Inflation rises but government silent",
    ]
    print("\n" + "="*60)
    print("🧪 TESTING GEN-Z HINGLISH TRANSLATION")
    print("="*60 + "\n")
    for i, text in enumerate(tests, 1):
        print(f"\n--- Test {i} ---")
        print(f"Input:  {text}")
        res = translate_to_hindi(text)
        pct = get_hindi_percentage(res)
        print(f"Output: {res}")
        print(f"Hindi%: {pct:.0f}%")
        print(f"Valid:  {'✅' if pct >= 50 else '❌'}")


def _demo_tweets():
    print("\n" + "="*60)
    print("🧪 TESTING IMPROVED MEANINGFUL TWEET GENERATION")
    print("="*60 + "\n")
    demos = [
        ("India launches space mission to Moon while roads full of potholes", "funny"),
        ("Delhi pollution reaches hazardous levels, government asks people to wear masks", "funny"),
        ("Government announces bullet train while local trains are overcrowded", "accountability"),
        ("Rajasthan paper leak scandal in exams triggers student protests", "accountability"),
        ("Inflation rises sharply but government remains silent on price control", "serious"),
        ("New AI chatbot launched while internet connectivity remains poor in rural areas", "serious"),
        ("Supreme Court questions prohibition law implementation in states", "accountability"),
    ]
    for topic, mode in demos:
        tw = make_tweet(topic=topic, mode=mode)
        print(f"\n📱 [{mode.upper()}]:\n{tw}\n")


if __name__ == "__main__":
    test_translation()
    _demo_tweets()
