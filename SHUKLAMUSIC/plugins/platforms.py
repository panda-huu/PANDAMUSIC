from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from SHUKLAMUSIC import app
from SHUKLAMUSIC.helpers import language
from config import BANNED_USERS, SUPPORT_CHAT

@app.on_message(filters.command(["platforms", "platform"]) & ~BANNED_USERS)
@language
async def platforms_cmd(client, message: Message, _):
    text = (
        "**❖ sᴜᴘᴘᴏʀᴛᴇᴅ ᴘʟᴀᴛғᴏʀᴍs**\n\n"
        "**๏ YouTube** — ʟɪɴᴋ / sᴇᴀʀᴄʜ\n"
        "**๏ Spotify** — ᴛʀᴀᴄᴋ / ᴘʟᴀʏʟɪsᴛ / ᴀʟʙᴜᴍ\n"
        "**๏ Apple Music** — ᴛʀᴀᴄᴋ / ᴘʟᴀʏʟɪsᴛ\n"
        "**๏ SoundCloud** — ᴛʀᴀᴄᴋ\n"
        "**๏ Resso** — ᴛʀᴀᴄᴋ\n"
        "**๏ Telegram** — ᴀᴜᴅɪᴏ / ᴠɪᴅᴇᴏ ғɪʟᴇ\n"
        "**๏ M3u8 / Index** — ʟɪᴠᴇ sᴛʀᴇᴀᴍ\n\n"
        f"**๏ ᴜsᴇ** `/play` **ᴏʀ** `/vplay` **ᴡɪᴛʜ ᴀɴʏ ʟɪɴᴋ ᴏʀ sᴏɴɢ ɴᴀᴍᴇ.**"
    )
    await message.reply_text(text, reply_markup=InlineKeyboardMarkup(
        [[InlineKeyboardButton("» sᴜᴘᴘᴏʀᴛ", url=SUPPORT_CHAT)]]
    ))
