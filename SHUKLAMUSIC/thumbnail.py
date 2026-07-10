from PIL import Image, ImageDraw, ImageFont, ImageFilter
from io import BytesIO
import asyncio
import textwrap
import requests
import os

BASE_DIR  = os.path.dirname(os.path.abspath(__file__))
FONT_PATH = os.path.join(BASE_DIR, "fonts", "SMALL.ttf")
BG_IMAGE  = os.path.join(BASE_DIR, "static", "BG.jpg")

OWNER   = "@ll_PANDA_BBY_ll"
CHANNEL = "ARU X API [BOTS]"


def sec_to_time(sec):
    try:
        sec = int(sec)
        return f"{sec // 60}:{sec % 60:02d}"
    except Exception:
        return "0:00"


def load_font(size):
    try:
        return ImageFont.truetype(FONT_PATH, size)
    except Exception:
        try:
            return ImageFont.truetype(
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size
            )
        except Exception:
            return ImageFont.load_default()


def fetch_image_sync(url):
    try:
        r = requests.get(url, timeout=8)
        return Image.open(BytesIO(r.content)).convert("RGB")
    except Exception:
        return None


def rounded_paste(canvas, img, pos, radius=28, border=6, border_color="white"):
    size = img.size
    border_size = (size[0] + border * 2, size[1] + border * 2)
    border_img  = Image.new("RGBA", border_size, (0, 0, 0, 0))
    b_mask      = Image.new("L", border_size, 0)
    ImageDraw.Draw(b_mask).rounded_rectangle(
        [0, 0, border_size[0], border_size[1]], radius=radius + border, fill=255
    )
    border_layer = Image.new("RGBA", border_size, border_color)
    border_img.paste(border_layer, mask=b_mask)
    canvas.paste(border_img, (pos[0] - border, pos[1] - border), border_img)

    mask   = Image.new("L", size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, size[0], size[1]], radius=radius, fill=255)
    output = Image.new("RGBA", size, (0, 0, 0, 0))
    output.paste(img, mask=mask)
    canvas.paste(output, pos, output)


def _build_thumbnail(song_json):
    """Sync thumbnail builder — runs in executor."""
    song      = song_json.get("song",     "Unknown Song")
    artist    = song_json.get("artist",   "")
    duration  = sec_to_time(song_json.get("duration", 0))
    views     = song_json.get("views",    "")
    image_url = song_json.get("image",    "")

    W, H   = 1280, 540
    bg_raw = Image.open(BG_IMAGE).convert("RGB").resize((W, H))
    bg_blur = bg_raw.filter(ImageFilter.GaussianBlur(radius=18))
    dark    = Image.new("RGB", (W, H), (0, 0, 0))
    canvas  = Image.blend(bg_blur, dark, alpha=0.55).convert("RGBA")

    # Album art
    art_size = 340
    art_x    = 90
    art_y    = (H - art_size) // 2
    album_art = fetch_image_sync(image_url)
    if album_art:
        album_art = album_art.resize((art_size, art_size))
    else:
        album_art = Image.new("RGB", (art_size, art_size), (50, 50, 80))
    rounded_paste(canvas, album_art, (art_x, art_y))

    # Info card
    card_x = art_x + art_size + 70
    card_y = 60
    card_w = W - card_x - 60
    card_h = H - card_y * 2
    card_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(card_layer).rounded_rectangle(
        [card_x, card_y, card_x + card_w, card_y + card_h],
        radius=24, fill=(40, 42, 50, 210)
    )
    canvas = Image.alpha_composite(canvas, card_layer)
    draw   = ImageDraw.Draw(canvas)

    # Fonts
    title_font  = load_font(58)
    artist_font = load_font(34)
    views_font  = load_font(30)
    time_font   = load_font(28)
    tag_font    = load_font(20)

    tx = card_x + 35
    ty = card_y + 38

    # Title
    for line in textwrap.wrap(song, width=20)[:2]:
        draw.text((tx, ty), line, font=title_font, fill="white")
        ty += 66

    # Artist
    ty += 4
    if artist:
        artist_short = (artist[:38] + "...") if len(artist) > 38 else artist
        draw.text((tx, ty), f"By {artist_short}", font=artist_font, fill="white")
        ty += 50

    # Views
    if views:
        draw.text((tx, ty), f"Views: {views}", font=views_font, fill="white")
        ty += 46

    ty += 10

    # Progress bar
    bar_x = tx
    bar_y = ty + 20
    bar_w = card_w - 70
    bar_h = 8

    draw.rounded_rectangle([bar_x, bar_y, bar_x + bar_w, bar_y + bar_h],
                            radius=bar_h // 2, fill=(100, 100, 120))
    fill_w = int(bar_w * 0.12)
    draw.rounded_rectangle([bar_x, bar_y, bar_x + fill_w, bar_y + bar_h],
                            radius=bar_h // 2, fill=(0, 191, 255))
    thumb_cx = bar_x + fill_w
    thumb_cy = bar_y + bar_h // 2
    r = 10
    draw.ellipse([thumb_cx - r, thumb_cy - r, thumb_cx + r, thumb_cy + r], fill="white")

    # Time
    time_y = bar_y + bar_h + 14
    draw.text((bar_x, time_y), "0:00", font=time_font, fill="white")
    dur_box = draw.textbbox((0, 0), duration, font=time_font)
    draw.text((bar_x + bar_w - (dur_box[2] - dur_box[0]), time_y), duration,
              font=time_font, fill="white")

    # Watermark
    wm_y    = H - 36
    powered = f"Powered by {CHANNEL}"
    draw.text((20, wm_y), OWNER, font=tag_font, fill=(200, 200, 200))
    pw_box = draw.textbbox((0, 0), powered, font=tag_font)
    draw.text((W - (pw_box[2] - pw_box[0]) - 20, wm_y), powered,
              font=tag_font, fill=(150, 150, 160))

    img_io = BytesIO()
    canvas.convert("RGB").save(img_io, "PNG")
    img_io.seek(0)
    return img_io


async def generate_thumbnail(song_json):
    """Async wrapper — runs sync builder in thread executor."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _build_thumbnail, song_json)
