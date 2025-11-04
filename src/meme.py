from PIL import Image, ImageDraw, ImageFont
import os
from .config import CONFIG
from .utils import wrap_for_meme, mkhash

def _try_load_font(path: str, size: int):
    if not path:
        return None
    try:
        return ImageFont.truetype(path, size=size)
    except Exception:
        return None

def _load_hindi_font(img_width: int):
    """
    Load a Devanagari-capable font for Hindi + basic emoji glyphs.
    Color emojis may not render (Pillow limitation), but unicode emoji
    will at least fall back to monochrome on most systems.
    """
    base_size = max(20, int(img_width * 0.045))

    # 1) Explicit font path via env
    env_path = os.getenv("MEME_FONT_PATH", "").strip()
    f = _try_load_font(env_path, base_size)
    if f: return f

    # 2) Windows common Hindi fonts
    for p in [
        "C:\\Windows\\Fonts\\Nirmala.ttf",
        "C:\\Windows\\Fonts\\NirmalaUI.ttf",
        "C:\\Windows\\Fonts\\Mangal.ttf",
    ]:
        f = _try_load_font(p, base_size)
        if f: return f

    # 3) Linux common
    for p in [
        "/usr/share/fonts/truetype/noto/NotoSansDevanagari-Regular.ttf",
        "/usr/share/fonts/truetype/noto/NotoSerifDevanagari-Regular.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSerif.ttf",
    ]:
        f = _try_load_font(p, base_size)
        if f: return f

    # 4) Fallback
    for p in ["arial.ttf"]:
        f = _try_load_font(p, base_size)
        if f: return f

    return ImageFont.load_default()

def _autofit_lines(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, W: int, H: int):
    """
    Auto-wrap + shrink font to fit in lower third of the image.
    """
    max_width_px = int(W * 0.9)
    y_top = int(H * 0.65)
    y_max = int(H * 0.95)

    size = getattr(font, "size", 24)

    def wrapped(w_chars):
        return wrap_for_meme(text, width=w_chars).split("\n")

    def chars_for_size(s):
        avg_char_px = s * 0.6  # heuristic
        return max(8, int(max_width_px / max(1, avg_char_px)))

    while size >= 16:
        test_font = ImageFont.truetype(font.path, size=size) if hasattr(font, "path") else font.font_variant(size=size)
        lines = wrapped(chars_for_size(size))
        y = y_top
        ok = True
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=test_font)
            w, h = bbox[2], bbox[3]
            if w > max_width_px or (y + h) > y_max:
                ok = False
                break
            y += int(h * 1.2)
        if ok:
            return test_font, lines, y_top
        size -= 2

    return (font.font_variant(size=16) if hasattr(font, "font_variant") else font), [text], y_top

def make_meme(text: str) -> tuple[str, str]:
    template = CONFIG["posting"]["meme_template"]
    img = Image.open(template).convert("RGB")
    W, H = img.size
    draw = ImageDraw.Draw(img)

    font = _load_hindi_font(W)
    font, lines, y = _autofit_lines(draw, text, font, W, H)

    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        w, h = bbox[2], bbox[3]
        x = (W - w) // 2
        draw.text(
            (x, y),
            line,
            font=font,
            fill=(255, 255, 255),
            stroke_width=3,
            stroke_fill=(0, 0, 0),
        )
        y += int(h * 1.2)

    os.makedirs("out", exist_ok=True)
    media_hash = mkhash(text, template)
    path = f"out/meme_{media_hash}.jpg"
    img.save(path, "JPEG", quality=90)
    return path, media_hash
