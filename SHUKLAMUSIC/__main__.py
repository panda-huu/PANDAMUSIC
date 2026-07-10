
import asyncio
import importlib
import os

from pyrogram import idle
from pytgcalls.exceptions import NoActiveGroupCall

import config
from config import BANNED_USERS
from SHUKLAMUSIC import LOGGER, app, userbot
from SHUKLAMUSIC.core.call import SHUKLA
from SHUKLAMUSIC.plugins import ALL_MODULES
from SHUKLAMUSIC.helpers import get_banned_users, get_gbanned
from SHUKLAMUSIC.database import init_db


async def init():
    if (
        not config.STRING1
        and not config.STRING2
        and not config.STRING3
        and not config.STRING4
        and not config.STRING5
    ):
        LOGGER(__name__).error("String Session Not Filled, Please Fill A Pyrogram Session")
        exit()

    await init_db()
    try:
        users = await get_gbanned()
        for user_id in users:
            BANNED_USERS.add(user_id)
        users = await get_banned_users()
        for user_id in users:
            BANNED_USERS.add(user_id)
    except Exception:
        pass

    await app.start()
    bot_info = await app.get_me()
    app.username = bot_info.username
    app.mention  = bot_info.mention

    for all_module in ALL_MODULES:
        importlib.import_module("SHUKLAMUSIC.plugins" + all_module)

    LOGGER("SHUKLAMUSIC.plugins").info("All Features Loaded Baby...")
    await userbot.start()
    await SHUKLA.start()

    try:
        await SHUKLA.stream_call("https://te.legra.ph/file/29f784eb49d230ab62e9e.mp4")
    except NoActiveGroupCall:
        LOGGER("SHUKLAMUSIC").error("PlZ START YOUR LOG GROUP VOICECHAT\nSTRANGER BOT STOP........")
        exit()
    except Exception:
        pass

    await SHUKLA.decorators()

    os.system("clear")
    print("""
╔════════════════════════════════╗
║                                  
║     ʀᴀᴅʜᴇ ᴍᴜsɪᴄ sᴛᴀʀᴛᴇᴅ 🎵      
║                                  
║     ᴘʀᴇᴍ sᴇ ʙᴏʟɪʏᴇ 🙏            
║     ʀᴀᴅʜᴇ ʀᴀᴅʜᴇ                 
║                                  
║     ʀᴇɢᴀʀᴅᴇᴅ ʙʏ ᴘᴀɴᴅᴀ ʙᴀʙʏ 👑   
║                                  
╚════════════════════════════════╝
""")

    await idle()
    await app.stop()
    await userbot.stop()
    LOGGER("SHUKLAMUSIC").info("BOT STOPPED")


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(init())
