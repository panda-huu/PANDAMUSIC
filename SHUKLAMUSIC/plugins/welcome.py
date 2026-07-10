"""
SHUKLAMUSIC/plugins/welcome.py
"""
import asyncio
import random
import traceback

from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from pyrogram.enums import ParseMode

import config
from SHUKLAMUSIC import app

WELCOME_IMAGES = [
    "https://files.catbox.moe/nacfzm.jpg",
    "https://files.catbox.moe/x4lzbx.jpg",
    "https://files.catbox.moe/g6cmb2.jpg",
    "https://files.catbox.moe/3hxb96.jpg",
]

WELCOME_TEXT = """🌸✨ ──────────────────── ✨🌸
🌹 <b>ɴᴀᴍᴇ</b> ➤ {name}
🆔 <b>ᴜsᴇʀ ɪᴅ</b> ➤ <code>{user_id}</code>
🏠 <b>ɢʀᴏᴜᴘ</b> ➤ {chat_title}
🌸✨ ──────────────────── ✨🌸
"""


async def _delete_later(msg, delay: int):
    await asyncio.sleep(delay)
    try:
        await msg.delete()
    except Exception:
        pass


@app.on_message(filters.new_chat_members & filters.group, group=99)
async def welcome_new_member(client, message: Message):
    print(f"[WELCOME] EVENT FIRED in chat {message.chat.id} | members: {[u.id for u in message.new_chat_members]}")

    try:
        chat_id    = message.chat.id
        chat_title = message.chat.title or "ᴛʜɪs ɢʀᴏᴜᴘ"

        for user in message.new_chat_members:
            print(f"[WELCOME] processing user {user.id} ({user.first_name}) is_bot={user.is_bot}")

            if user.id == client.me.id or user.is_bot:
                print("[WELCOME] skipped (bot itself or another bot)")
                continue

            name    = user.first_name or "User"
            user_id = user.id

            photo   = random.choice(WELCOME_IMAGES)
            caption = WELCOME_TEXT.format(name=name, user_id=user_id, chat_title=chat_title)
            buttons = InlineKeyboardMarkup([
                [InlineKeyboardButton("• ᴜᴩᴅᴀᴛᴇs •", url=config.SUPPORT_CHANNEL)]
            ])

            print(f"[WELCOME] sending photo to {chat_id} ...")
            wel = await client.send_photo(
                chat_id,
                photo=photo,
                caption=caption,
                parse_mode=ParseMode.HTML,
                reply_markup=buttons,
            )
            print("[WELCOME] photo sent successfully ✅")
            asyncio.create_task(_delete_later(wel, 300))

    except Exception:
        print("[WELCOME] ❌ EXCEPTION:")
        traceback.print_exc()
