import re
from pyrogram import filters

# ─── Database ───────────────────────────────────────────────────────────────
DATABASE_URL      = "postgresql://postgres.wdenzjnjtytuvwfzisci@aws-1-ap-southeast-2.pooler.supabase.com:6543/postgres"
DATABASE_PASSWORD = "nikitayt7?#Rhu"  # password alag rakha — special chars safe
# ↑ Upar <PASSWORD> ki jagah apna actual Supabase password daalo

# ─── Required ───────────────────────────────────────────────────────────────
API_ID    = API_ID          # your api id
API_HASH  = "YOUR_API_HASH"         # your api hash
BOT_TOKEN = "YOUR_BOT_TOKEN"         # your bot token

# ─── Owner & Bot Info ────────────────────────────────────────────────────────
OWNER_ID       = 7450385463              # your telegram user id
OWNER_USERNAME = "ll_PANDA_BBY_ll" # without @
BOT_NAME       = "ꪹꪖᦔꫝꪖ ꪑꪊకỉᨶ ꪉꪮᡶ"
BOT_USERNAME   = "SUKRITI_MUSIC_BOT"

# ─── Logger ──────────────────────────────────────────────────────────────────
LOGGER_ID = -1003468477782  # log channel id (negative number)

# ─── Support ─────────────────────────────────────────────────────────────────
SUPPORT_CHANNEL = "https://t.me/sxypndu"
SUPPORT_CHAT    = "https://t.me/+hXQIhjEPfC1jZTY1"

# ─── Assistant Session Strings ───────────────────────────────────────────────
STRING1 = "YOUR_STRING_SESSION"
STRING2 = ""  # optional
STRING3 = ""  # optional
STRING4 = ""  # optional
STRING5 = ""  # optional

# ─── Spotify ─────────────────────────────────────────────────────────────────
SPOTIFY_CLIENT_ID     = ""
SPOTIFY_CLIENT_SECRET = ""

# ─── Limits ──────────────────────────────────────────────────────────────────
DURATION_LIMIT_MIN           = 9999
PLAYLIST_FETCH_LIMIT         = 25
SONG_DOWNLOAD_DURATION       = 9999999
SONG_DOWNLOAD_DURATION_LIMIT = 9999999
TG_AUDIO_FILESIZE_LIMIT      = 5242880000
TG_VIDEO_FILESIZE_LIMIT      = 5242880000

# ─── Images ──────────────────────────────────────────────────────────────────
START_IMG_URL            = "https://files.catbox.moe/ak96mx.jpg"
PING_IMG_URL             = "https://files.catbox.moe/ak96mx.jpg"
PLAYLIST_IMG_URL         = "https://files.catbox.moe/lrwbj6.jpg"
STREAM_IMG_URL           = "https://files.catbox.moe/aesldg.jpg"
YOUTUBE_IMG_URL          = "https://files.catbox.moe/aesldg.jpg"
SPOTIFY_ARTIST_IMG_URL   = "https://files.catbox.moe/aesldg.jpg"
SPOTIFY_ALBUM_IMG_URL    = "https://files.catbox.moe/aesldg.jpg"
SPOTIFY_PLAYLIST_IMG_URL = "https://files.catbox.moe/aesldg.jpg"
TELEGRAM_AUDIO_URL       = "https://files.catbox.moe/aesldg.jpg"
TELEGRAM_VIDEO_URL       = "https://files.catbox.moe/aesldg.jpg"
SOUNDCLOUD_IMG_URL       = "https://files.catbox.moe/aesldg.jpg"
SOUNCLOUD_IMG_URL        = SOUNDCLOUD_IMG_URL  # alias (typo in some files)
STATS_IMG_URL            = "https://files.catbox.moe/ak96mx.jpg"
SHASHANK_IMG             = [
    "https://files.catbox.moe/ak96mx.jpg",
    "https://files.catbox.moe/aesldg.jpg",
    "https://files.catbox.moe/lrwbj6.jpg",
]

# ─── Extra / Optional ────────────────────────────────────────────────────────
SUPPORT_GROUP      = SUPPORT_CHAT
DEBUG_IGNORE_LOG   = False
S_B_2              = ""
S_B_5              = ""
S_B_6              = ""
S_B_9              = ""

# ─── Internal ────────────────────────────────────────────────────────────────
BANNED_USERS = filters.user()
adminlist    = {}
lyrical      = {}
votemode     = {}
autoclean    = []
confirmer    = {}

def time_to_seconds(time: str) -> int:
    return sum(int(x) * 60**i for i, x in enumerate(reversed(time.split(":"))))

DURATION_LIMIT = int(time_to_seconds(f"{DURATION_LIMIT_MIN}:00"))

if not re.match(r"(?:http|https)://", SUPPORT_CHANNEL):
    raise SystemExit("[ERROR] SUPPORT_CHANNEL url invalid")
if not re.match(r"(?:http|https)://", SUPPORT_CHAT):
    raise SystemExit("[ERROR] SUPPORT_CHAT url invalid")

# ── Missing value used in stats.py ──────────────────────────────────────────
AUTO_LEAVING_ASSISTANT = False
