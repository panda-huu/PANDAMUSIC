# ---------------------------------------------------------------
# 🔸 RADHExMUSIC — blacklist.py
# 🔹 /blacklist <word>   — add word
# 🔹 /unblacklist <word> — remove word
# 🔹 /blacklistview      — list all words
# ---------------------------------------------------------------

import json
import os
import re

from pyrogram import filters
from pyrogram.enums import ChatMemberStatus
from pyrogram.types import Message

from SHUKLAMUSIC import app

# ── Persistent JSON file ──────────────────────────────────────────────────────
_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "blacklist_db.json")

def _load() -> dict:
    try:
        if os.path.exists(_DB_PATH):
            with open(_DB_PATH, "r") as f:
                return json.load(f)
    except Exception:
        pass
    return {}

def _save(data: dict):
    try:
        with open(_DB_PATH, "w") as f:
            json.dump(data, f)
    except Exception:
        pass

def _get_words(chat_id: int) -> list:
    data = _load()
    return data.get(str(chat_id), [])

def _add_word(chat_id: int, word: str) -> bool:
    data = _load()
    key  = str(chat_id)
    if key not in data:
        data[key] = []
    word = word.lower().strip()
    if word in data[key]:
        return False  # already exists
    data[key].append(word)
    _save(data)
    return True

def _remove_word(chat_id: int, word: str) -> bool:
    data = _load()
    key  = str(chat_id)
    word = word.lower().strip()
    if key not in data or word not in data[key]:
        return False
    data[key].remove(word)
    _save(data)
    return True

def _matches_blacklist(text: str, words: list) -> bool:
    if not text or not words:
        return False
    text_lower = text.lower()
    for w in words:
        pattern = r"(?<![a-zA-Z0-9])" + re.escape(w) + r"(?![a-zA-Z0-9])"
        if re.search(pattern, text_lower):
            return True
    return False

# ── Helper: check admin ───────────────────────────────────────────────────────
async def _is_admin(client, chat_id: int, user_id: int) -> bool:
    try:
        m = await client.get_chat_member(chat_id, user_id)
        return m.status in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER)
    except Exception:
        return False


# ── /blacklist <word> ─────────────────────────────────────────────────────────
@app.on_message(filters.command("blacklist") & filters.group)
async def blacklist_add(client, msg: Message):
    try:
        await message.delete()
    except Exception:
        pass
    if not await _is_admin(client, msg.chat.id, msg.from_user.id):
        return await msg.reply("❌ <b>ꜱɪʀꜰ ᴀᴅᴍɪɴ ɪsᴛᴇᴍᴀᴀʟ ᴋᴀʀ ꜱᴀᴋᴛᴇ ʜᴀɪɴ!</b>")

    if len(msg.command) < 2:
        return await msg.reply(
            "❓ <b>ᴜsᴀɢᴇ:</b>\n"
            "<code>/blacklist &lt;word&gt;</code>\n\n"
            "<b>ᴇxᴀᴍᴘʟᴇ:</b> <code>/blacklist badword</code>"
        )

    word = " ".join(msg.command[1:]).lower().strip()
    if len(word) < 2:
        return await msg.reply("❌ <b>ᴡᴏʀᴅ ᴄʜᴏᴛᴀ ʜᴀɪ, ᴋᴀᴍ sᴇ ᴋᴀᴍ 2 ᴄʜᴀʀ ʟɪᴋʜᴏ!</b>")

    added = _add_word(msg.chat.id, word)
    if added:
        await msg.reply(
            f"✅ <b>ʙʟᴀᴄᴋʟɪsᴛ ᴍᴇɪɴ ᴀᴅᴅ ʜᴏ ɢᴀʏᴀ!</b>\n\n"
            f"🚫 <b>ᴡᴏʀᴅ:</b> <code>{word}</code>\n\n"
            f"<i>ᴀʙ ʏᴇ ᴡᴏʀᴅ ᴋᴏɪ ʙʜɪ ʟɪᴋʜᴇɢᴀ ᴛᴏ ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ ʜᴏɢᴀ.</i>"
        )
    else:
        await msg.reply(
            f"⚠️ <b>ʏᴇ ᴡᴏʀᴅ ᴘᴀʜʟᴇ ʜɪ ʙʟᴀᴄᴋʟɪsᴛ ᴍᴇɪɴ ʜᴀɪ!</b>\n\n"
            f"🚫 <code>{word}</code>"
        )


# ── /unblacklist <word> ───────────────────────────────────────────────────────
@app.on_message(filters.command("unblacklist") & filters.group)
async def blacklist_remove(client, msg: Message):
    try:
        await message.delete()
    except Exception:
        pass
    if not await _is_admin(client, msg.chat.id, msg.from_user.id):
        return await msg.reply("❌ <b>ꜱɪʀꜰ ᴀᴅᴍɪɴ ɪsᴛᴇᴍᴀᴀʟ ᴋᴀʀ ꜱᴀᴋᴛᴇ ʜᴀɪɴ!</b>")

    if len(msg.command) < 2:
        return await msg.reply(
            "❓ <b>ᴜsᴀɢᴇ:</b> <code>/unblacklist &lt;word&gt;</code>"
        )

    word = " ".join(msg.command[1:]).lower().strip()
    removed = _remove_word(msg.chat.id, word)
    if removed:
        await msg.reply(
            f"✅ <b>ʀᴇᴍᴏᴠᴇᴅ ꜰʀᴏᴍ ʙʟᴀᴄᴋʟɪsᴛ!</b>\n\n"
            f"🗑 <code>{word}</code>"
        )
    else:
        await msg.reply(
            f"❌ <b>ʏᴇ ᴡᴏʀᴅ ʙʟᴀᴄᴋʟɪsᴛ ᴍᴇɪɴ ʜᴀɪ ʜɪ ɴᴀʜɪ!</b>\n\n"
            f"<code>{word}</code>"
        )


# ── /blacklistview ────────────────────────────────────────────────────────────
@app.on_message(filters.command("blacklistview") & filters.group)
async def blacklist_view(client, msg: Message):
    try:
        await message.delete()
    except Exception:
        pass
    if not await _is_admin(client, msg.chat.id, msg.from_user.id):
        return await msg.reply("❌ <b>ꜱɪʀꜰ ᴀᴅᴍɪɴ ɪsᴛᴇᴍᴀᴀʟ ᴋᴀʀ ꜱᴀᴋᴛᴇ ʜᴀɪɴ!</b>")

    words = _get_words(msg.chat.id)
    if not words:
        return await msg.reply(
            "📋 <b>ʙʟᴀᴄᴋʟɪsᴛ ᴇᴍᴘᴛʏ ʜᴀɪ!</b>\n\n"
            "<i>ᴀᴅᴅ ᴋᴀʀɴᴇ ᴋᴇ ʟɪʏᴇ:</i> <code>/blacklist &lt;word&gt;</code>"
        )

    word_list = "\n".join(f"  • <code>{w}</code>" for w in words)
    await msg.reply(
        f"📋 <b>ʙʟᴀᴄᴋʟɪsᴛᴇᴅ ᴡᴏʀᴅs — {msg.chat.title}</b>\n\n"
        f"{word_list}\n\n"
        f"<b>ᴛᴏᴛᴀʟ:</b> {len(words)} ᴡᴏʀᴅs"
    )


# ── Detection is handled by noabuse.py watcher (merged) ─────────────────────
# blacklist.py sirf add/remove/view commands handle karta hai
