import random
from datetime import datetime
from pyrogram import filters
from pyrogram.types import Message
import config
from SHUKLAMUSIC import app
from SHUKLAMUSIC.core.call import SHUKLA
from SHUKLAMUSIC.helpers import language, bot_sys_stats, supp_markup
from config import BANNED_USERS, SHASHANK_IMG

@app.on_message(filters.command("ping") & ~BANNED_USERS)
@language
async def ping_com(client, message: Message, _):
    try:                        # ← yahan se
        await message.delete()
    except Exception:
        pass
    start = datetime.now()
    response = await message.reply_photo(random.choice(SHASHANK_IMG), caption=_["ping_1"].format(f"@{config.BOT_USERNAME}"))
    pytgping = await SHUKLA.ping()
    UP, CPU, RAM, DISK = await bot_sys_stats()
    resp = (datetime.now() - start).microseconds / 1000
    await response.edit_text(
        _["ping_2"].format(resp, f"@{config.BOT_USERNAME}", UP, RAM, CPU, DISK, pytgping),
        reply_markup=supp_markup(_),
    )
