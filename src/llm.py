# ✅ src/llm.py — Gen-Z Hinglish Tweet Generator (Poetic, Sarcastic, Comedy)

from .config import CONFIG
from .utils import safe_tweet, hashtagify, detox, is_sensitive
import re
import time
from groq import Groq


# ---------------------- STYLE PROMPTS (Gen-Z, Hinglish, Poetic, Sarcastic, Comedy) -------------------------

FUNNY_STYLE_HI = (
    "तुम एक Gen-Z स्टाइल के न्यूज़ रिपोर्टर हो जो खबरें थोड़ा तंज, थोड़ा मीम-वाइब और relatable अंदाज़े में सुनाता है। "
    "भाषा हिंदी (देवनागरी) हो लेकिन कुछ रोज़े के English/tech words जैसे bro, system, AI, update, cringe, scene, app, data, scam, legit, hack, vibe, mood, flex, salty, toxic, lit use कर सकते हो। "
    "North India वाला हल्का flavor चलेगा — जैसे 'अरे भाई', 'यार ये क्या हो रहा है', 'सिस्टम फिर लटक गया', 'अभी update ही आया है'। "
    "Sarcasm, poetic lines, और comedy mix करो — लेकिन किसी की insult, religion, caste या sensitive मुद्दे का मज़ाक नहीं। "
    "मज़े के emojis जैसे 😭 😅 🔥 🤦‍♂️ 💀 😤 🙃 ✨ use कर सकते हो (1-2 ही)। "
    "Numbers हमेशा English: 1, 2, 3, 4, 5। "
    "हैशटैग मत जोड़ो। 280 characters से कम।"
)

SERIOUS_STYLE_HI = (
    "तुम एक calm और responsible Gen-Z न्यूज़ राइटर हो। "
    "भाषा मुख्यतः हिंदी (देवनागरी) हो लेकिन basic English words जैसे update, report, data, system, mission, train, school use कर सकते हो। "
    "टोन neutral, सम्मानजनक, fact-based हो लेकिन थोड़ा poetic या thoughtful tone भी ठीक है। "
    "कोई emoji नहीं, कोई over-dramatic tone नहीं लेकिन sarcasm mild हो सकता है। "
    "Numbers English में: 1, 2, 3। "
    "हैशटैग मत जोड़ो। 280 characters में।"
)

ACCOUNTABILITY_STYLE_HI = (
    "तुम एक शांत लेकिन सच्चाई बोलने वाले जनहित पत्रकार हो जो poetic और powerful है। "
    "पूरी भाषा हिंदी (देवनागरी) लेकिन system, data, update जैसे words ठीक हैं। "
    "अगर सरकार, सिस्टम या प्रशासन की कमी दिखे तो respectfully लेकिन सीधे सवाल उठा सकते हो — जैसे "
    "'जवाब कौन देगा?', 'लोग परेशान हैं', 'ये ठीक नहीं है', 'कब तक इंतज़ार?'। "
    "Poetic, emotional, सarcastic tone acceptable है लेकिन गाली, blame-game या hate नहीं। "
    "1 emoji (😐 😔 💔 ❌) तक ठीक है। "
    "Numbers: 1, 2, 3 (English)। "
    "हैशटैग मत जोड़ो। 280 characters।"
)

TRANSLATE_TO_HINDI_PROMPT = (
    "इस वाक्य को simple और natural हिंदी में बदलो। Gen-Z style हो सकता है। "
    "जहां ज़रूरी हो वहां daily English या tech words जैसे system, data, update, AI, mission, train, school, app, hack use कर सकते हो। "
    "Sarcasm, comedy या poetic feeling जोड़ सकते हो अगर बेहतर हो। "
    "Numbers हमेशा English: 1, 2, 3, 4, 5। "
    "केवल अनुवाद दो।\n\n"
    "वाक्य:\n"
)

# Common Gen-Z English words allowed
GEN_Z_WORDS = [
    "bro", "system", "AI", "update", "cringe", "scene", "app", "data", "scam", "legit", "hack",
    "vibe", "mood", "flex", "salty", "toxic", "lit", "slay", "sarcasm", "drama", "catch",
    "mission", "train", "school", "college", "job", "boss", "team", "fail", "win", "level",
    "report", "news", "break", "shock", "alert", "tweet", "share", "follow", "like", "comment"
]


# ---------------------- HINDI DETECTION -------------------------
def contains_hindi(text: str) -> bool:
    """Check if text contains Devanagari script"""
    if not text:
        return False
    return bool(re.search(r'[\u0900-\u097F]', text))


def get_hindi_percentage(text: str) -> float:
    """Calculate percentage of Hindi characters"""
    if not text:
        return 0.0
    
    text_clean = re.sub(r'[\s.,;:!?\n\r-0-9]', '', text)
    if not text_clean:
        return 0.0
    
    hindi_chars = len(re.findall(r'[\u0900-\u097F]', text_clean))
    total_chars = len(text_clean)
    
    return (hindi_chars / total_chars * 100) if total_chars > 0 else 0.0


def normalize_numbers(text: str) -> str:
    """Replace Hindi numerals with English numerals"""
    hindi_to_english = {
        '०': '0', '१': '1', '२': '2', '३': '3', '४': '4',
        '५': '5', '६': '6', '७': '7', '८': '8', '९': '9'
    }
    for hindi, english in hindi_to_english.items():
        text = text.replace(hindi, english)
    return text


# ---------------------- GROQ CALLER -------------------------

def call_groq(prompt: str, system: str = None) -> str:
    """Simple, working Groq call with Gen-Z vibes"""
    try:
        client = Groq(api_key=CONFIG["llm"]["groq_api_key"])
        
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages,
            temperature=0.8,  # Higher for more creativity and poetic tone
            max_tokens=512,
        )
        
        result = completion.choices[0].message.content.strip()
        return normalize_numbers(result)
    
    except Exception as e:
        print(f"❌ Groq Error: {e}")
        return ""


# ---------------------- HINDI TRANSLATION -------------------------

def translate_to_hindi(text: str) -> str:
    """Translate text to Hindi with Gen-Z, poetic, sarcastic vibes"""
    
    if not text or not text.strip():
        return ""
    
    # Skip if already mostly Hindi
    if get_hindi_percentage(text) > 80:
        return normalize_numbers(text.strip())
    
    print(f"🔄 Translating to Hinglish: {text[:60]}...")
    
    prompt = f"{TRANSLATE_TO_HINDI_PROMPT}{text}"
    system = (
        "You are a Gen-Z Hindi translator. "
        "Write MOSTLY in Hindi (Devanagari script). "
        "You can use common English words like: bro, system, AI, update, cringe, scene, app, data, scam, legit, hack, vibe, mood, flex, salty, toxic, lit, slay, drama, mission, train, school, college, job, boss, team, fail, win. "
        "Be poetic, sarcastic, or funny when it fits. "
        "Use English numerals: 1, 2, 3, 4, 5 (NEVER use Hindi numerals like १, २, ३). "
        "Keep it natural, relatable, and Gen-Z vibes. "
        "ONE LINE ONLY."
    )
    
    result = call_groq(prompt, system)
    
    if result and contains_hindi(result):
        hindi_pct = get_hindi_percentage(result)
        if hindi_pct >= 50:
            print(f"✅ Translation success ({hindi_pct:.0f}% Hindi): {result[:60]}...")
            return result
        print(f"⚠ Low Hindi percentage: {hindi_pct:.0f}%")
    
    # Fallback
    print(f"❌ Translation failed")
    return f"📱 {text}"


# ---------------------- MAIN TWEET FUNCTION -------------------------

def make_tweet(
    topic: str, 
    link: str = None, 
    mode: str = "funny", 
    add_hashtags_from: str = None
) -> str:
    """Generate Gen-Z Hinglish tweet with poetic, sarcastic, comedy vibes"""
    
    if not topic or not topic.strip():
        return "⚠ अरे भाई, विषय तो दे दो! 😅"
    
    print(f"\n{'='*60}")
    print(f"🐦 Making tweet for: {topic[:60]}...")
    
    # Translate to Hinglish
    core = translate_to_hindi(topic)
    
    if not contains_hindi(core):
        print(f"⚠ Translation failed, using fallback")
        core = f"📱 {topic}"
    
    # Add link if provided
    if link:
        core = f"{core}\n\n🔗 {link}"
    
    # Check sensitivity
    sensitive = is_sensitive(core)
    if sensitive and mode == "funny":
        mode = "accountability" if CONFIG["safety"].get("critique_authorities") else "serious"
    
    # Select style
    style_map = {
        "funny": FUNNY_STYLE_HI,
        "serious": SERIOUS_STYLE_HI,
        "accountability": ACCOUNTABILITY_STYLE_HI
    }
    style = style_map.get(mode, FUNNY_STYLE_HI)
    
    # Generate tweet
    system_msg = (
        "You are a Gen-Z Hindi news writer. "
        "Write MOSTLY in Hindi Devanagari script. "
        "You can use: bro, system, AI, update, cringe, scene, app, data, scam, legit, hack, vibe, mood, flex, salty, toxic, lit, slay, drama, mission, train, school, college, job, boss, team, fail, win. "
        "Be poetic, sarcastic, funny, or dramatic as the situation demands. "
        "Use English numerals (1, 2, 3, 4, 5) NEVER Hindi numerals. "
        "Keep it natural, relatable, and Gen-Z vibes. "
        "North India flavor is welcome."
    )
    tweet_prompt = f"{style}\n\nविषय:\n{core}\n\nNow write a tweet:"
    
    try:
        tweet_text = call_groq(tweet_prompt, system_msg)
        
        if not tweet_text or not contains_hindi(tweet_text):
            print("⚠ LLM output invalid, using core text")
            tweet_text = core
        else:
            print(f"✅ Tweet generated: {tweet_text[:60]}...")
    
    except Exception as e:
        print(f"❌ Tweet generation failed: {e}")
        tweet_text = core
    
    # Apply content safety filter
    tweet_text = detox(tweet_text)
    
    # Add hashtags if requested
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
    
    # Combine and ensure length limit
    final_tweet = (tweet_text + " " + tags).strip()
    final_tweet = safe_tweet(final_tweet)
    final_tweet = normalize_numbers(final_tweet)
    
    # Final validation
    hindi_pct = get_hindi_percentage(final_tweet)
    print(f"✅ Final tweet ({len(final_tweet)} chars, {hindi_pct:.0f}% Hindi, Gen-Z vibes ✨):")
    print(f"   {final_tweet[:150]}...")
    print(f"{'='*60}\n")
    
    return final_tweet


# ---------------------- TESTING -------------------------

def test_translation():
    """Test function for debugging"""
    test_cases = [
        "Breaking news from Delhi government",
        "Police caught fake doctor scamming people",
        "New metro station opened in city",
        "Heavy rainfall damages roads",
        "Student protest for exam postponement"
    ]
    
    print("\n" + "="*60)
    print("🧪 TESTING GEN-Z HINGLISH TRANSLATION")
    print("="*60 + "\n")
    
    for i, text in enumerate(test_cases, 1):
        print(f"\n--- Test {i} ---")
        print(f"Input:  {text}")
        result = translate_to_hindi(text)
        hindi_pct = get_hindi_percentage(result)
        print(f"Output: {result}")
        print(f"Hindi%: {hindi_pct:.0f}%")
        print(f"Valid:  {'✅' if hindi_pct >= 50 else '❌'}")


if __name__ == "__main__":
    # Run tests
    test_translation()
    
    # Test full tweet generation
    print("\n" + "="*60)
    print("🧪 TESTING GEN-Z TWEET GENERATION")
    print("="*60 + "\n")
    
    tweets = [
        ("India launches new space mission to Moon", "funny"),
        ("Government fails to control pollution in Delhi", "accountability"),
        ("New AI chatbot launched for students", "serious"),
    ]
    
    for topic, mode in tweets:
        tweet = make_tweet(topic=topic, mode=mode)
        print(f"\n📱 [{mode.upper()}]:\n{tweet}\n")
