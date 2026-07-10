from pyrogram import filters, StopPropagation, ContinuePropagation
from pyrogram.types import Message

from SHUKLAMUSIC import app
from SHUKLAMUSIC.misc import SUDOERS
from config import BANNED_USERS

# ── Maintenance state ─────────────────────────────────────────────────────
MAINTENANCE_MODE: bool = False
MAINTENANCE_MSG: str = "🛠 **Bot is currently under maintenance.**\nPlease try again later."

PREFIXES = ("/", "!", ".", ",")


# ── /maintenance on | off (sirf sudo/owner ke liye) ───────────────────────
@app.on_message(filters.command(["maintenance"]) & ~BANNED_USERS, group=1)
async def maintenance_toggle(client, message: Message):
    global MAINTENANCE_MODE

    if message.from_user is None or message.from_user.id not in SUDOERS:
        return await message.reply_text("❌ Yeh command sirf bot owner/sudo users use kar sakte hain.")

    args = message.text.split(None, 1)
    if len(args) < 2:
        status = "ON ✅" if MAINTENANCE_MODE else "OFF ❌"
        return await message.reply_text(
            f"🛠 **Maintenance Mode:** {status}\n\n"
            "Usage:\n"
            "`/maintenance on` - Maintenance mode chalu karein\n"
            "`/maintenance off` - Maintenance mode band karein"
        )

    state = args[1].strip().lower()

    if state in ("on", "true", "enable", "1"):
        MAINTENANCE_MODE = True
        await message.reply_text("✅ **Maintenance mode ON kar diya gaya hai.**\nAb sirf sudo users hi bot use kar sakte hain.")
    elif state in ("off", "false", "disable", "0"):
        MAINTENANCE_MODE = False
        await message.reply_text("✅ **Maintenance mode OFF kar diya gaya hai.**\nBot ab normal kaam karega.")
    else:
        await message.reply_text("⚠️ Galat usage. `/maintenance on` ya `/maintenance off` use karein.")


# ── Global blocker — sabse pehle chalega (group=-1, sab handlers se pehle) ─
@app.on_message(filters.text, group=-1)
async def maintenance_blocker(client, message: Message):
    if not MAINTENANCE_MODE:
        raise ContinuePropagation

    if not message.text or not message.text.startswith(PREFIXES):
        raise ContinuePropagation

    if message.from_user and message.from_user.id in SUDOERS:
        raise ContinuePropagation

    cmd = message.text.split()[0][1:].split("@")[0].lower()
    if cmd == "maintenance":
        raise ContinuePropagation

    await message.reply_text(MAINTENANCE_MSG)
    raise StopPropagation
