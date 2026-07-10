import re
from pyrogram import filters

# ─── Database ───────────────────────────────────────────────────────────────
DATABASE_URL      = "postgresql://postgres.wdenzjnjtytuvwfzisci@aws-1-ap-southeast-2.pooler.supabase.com:6543/postgres"
DATABASE_PASSWORD = "nikitayt7?#Rhu"  # password alag rakha — special chars safe
# ↑ Upar <PASSWORD> ki jagah apna actual Supabase password daalo

# ─── Required ───────────────────────────────────────────────────────────────
API_ID    = 20898349          # your api id
API_HASH  = "9fdb830d1e435b785f536247f49e7d87"         # your api hash
BOT_TOKEN = "8800826100:AAFMZsDEjbGahJFTZTQuSjjfV9naowOEbi4"         # your bot token

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
STRING1 = "BQE-4i0AE85mujraUV1cYz_7p94nXFksmtOigac6hvrAMGis2u0DhtpYhmDg_dPkb9ulX0wopnZqGu8ivO9FFTilXfwCM4GrxrxjTk3zLgX6QXHVzd2jMJgxklB5Ykx_5-E-yo6Z6U6TRu2P_rskP1UaZQh7kOAfXoO7T9yX7VbjddmMONa72ShrY4tSHDRqWfJ34D4oSHlVneni-I5vlD_IIGS4_e3UaeO_O5c6Ch_Uy8brlWIRq6kNAtCVWXEAGT3-2PslU34u4pYyeRS2Pt7IIc1xyTYvR8CvFY4xP9_K_D3yoruFyhlCR6KFJimq7ahsC4_ld0mCbEupiglFWCuasokUuQAAAAHKarFXAA"
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
