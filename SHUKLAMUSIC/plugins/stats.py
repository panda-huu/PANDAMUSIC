import platform
from sys import version as pyver
import psutil
from pyrogram import __version__ as pyrover
from pyrogram import filters
from pyrogram.errors import MessageIdInvalid
from pyrogram.types import InputMediaPhoto, Message
from pytgcalls.__version__ import __version__ as pytgver
import config
from SHUKLAMUSIC import app
from SHUKLAMUSIC.core.userbot import assistants
from SHUKLAMUSIC.misc import SUDOERS
from SHUKLAMUSIC.helpers import (
    language, languageCB, get_served_chats, get_served_users, get_sudoers,
    stats_buttons, back_stats_buttons,
)
from config import BANNED_USERS

ALL_MODULES = ["start", "play", "ping", "stats", "platforms"]

@app.on_message(filters.command(["stats", "gstats"]) & filters.group & ~BANNED_USERS)
@language
async def stats_global(client, message: Message, _):
    try:                        # ← yahan se
        await message.delete()
    except Exception:
        pass
    await message.reply_photo(
        photo=config.STATS_IMG_URL,
        caption=_["gstats_2"].format(f"@{config.BOT_USERNAME}"),
        reply_markup=stats_buttons(_, message.from_user.id in SUDOERS),
    )

@app.on_callback_query(filters.regex("stats_back") & ~BANNED_USERS)
@languageCB
async def home_stats(client, cq, _):
    await cq.edit_message_text(
        text=_["gstats_2"].format(f"@{config.BOT_USERNAME}"),
        reply_markup=stats_buttons(_, cq.from_user.id in SUDOERS),
    )

@app.on_callback_query(filters.regex("TopOverall") & ~BANNED_USERS)
@languageCB
async def overall_stats(client, cq, _):
    try: await cq.answer()
    except: pass
    upl = back_stats_buttons(_)
    await cq.edit_message_text(_["gstats_1"].format(f"@{config.BOT_USERNAME}"))
    served_chats = len(await get_served_chats())
    served_users = len(await get_served_users())
    text = _["gstats_3"].format(
        f"@{config.BOT_USERNAME}", len(assistants), len(BANNED_USERS),
        served_chats, served_users, len(ALL_MODULES), len(SUDOERS),
        config.AUTO_LEAVING_ASSISTANT, config.DURATION_LIMIT_MIN,
    )
    med = InputMediaPhoto(media=config.STATS_IMG_URL, caption=text)
    try: await cq.edit_message_media(media=med, reply_markup=upl)
    except MessageIdInvalid:
        await cq.message.reply_photo(photo=config.STATS_IMG_URL, caption=text, reply_markup=upl)

@app.on_callback_query(filters.regex("bot_stats_sudo") & ~BANNED_USERS)
@languageCB
async def sudo_stats(client, cq, _):
    try: await cq.answer()
    except: pass
    if cq.from_user.id not in SUDOERS:
        return await cq.answer(_["gstats_4"], show_alert=True)
    await cq.edit_message_text(_["gstats_1"].format(f"@{config.BOT_USERNAME}"))
    served_chats = len(await get_served_chats())
    served_users = len(await get_served_users())
    sudoers_list = await get_sudoers()
    ram = psutil.virtual_memory()
    cpu_freq = psutil.cpu_freq()
    disk = psutil.disk_usage("/")
    from SHUKLAMUSIC.misc import SUDOERS as _SUDOERS
    try:
        from SHUKLAMUSIC.helpers import get_db_size
        db_size, db_storage, db_cols, db_keys = await get_db_size()
    except Exception:
        db_size = db_storage = db_cols = db_keys = "N/A"
    text = _["gstats_5"].format(
        f"@{config.BOT_USERNAME}",
        len(ALL_MODULES),
        platform.system(),
        f"{ram.used / (1024**3):.2f} / {ram.total / (1024**3):.2f} GiB",
        psutil.cpu_count(logical=False),
        psutil.cpu_count(logical=True),
        f"{cpu_freq.current:.0f} MHz" if cpu_freq else "N/A",
        pyver.split()[0],
        pyrover,
        pytgver,
        round(disk.free / (1024**3), 2),
        round(disk.used / (1024**3), 2),
        round((disk.free - disk.used) / (1024**3), 2) if disk.free > disk.used else 0,
        served_chats,
        served_users,
        len(config.BANNED_USERS),
        len(sudoers_list),
        db_size, db_storage, db_cols, db_keys,
    )
    upl = back_stats_buttons(_)
    med = InputMediaPhoto(media=config.STATS_IMG_URL, caption=text)
    try: await cq.edit_message_media(media=med, reply_markup=upl)
    except: await cq.message.reply_photo(photo=config.STATS_IMG_URL, caption=text, reply_markup=upl)
