# ---------------------------------------------------------------
# 🔸 RADHExMUSIC — tagall.py
# 🔹 /tagall — group admins sabko tag kar sakte hain.
# ---------------------------------------------------------------

import asyncio

from pyrogram import enums, filters
from pyrogram.errors import ChatAdminRequired, FloodWait
from pyrogram.types import Message

from SHUKLAMUSIC import app


async def _is_admin(client, chat_id, user_id):
    try:
        m = await client.get_chat_member(chat_id, user_id)
        return m.status in (
            enums.ChatMemberStatus.OWNER,
            enums.ChatMemberStatus.ADMINISTRATOR,
        )
    except Exception:
        return False


@app.on_message(filters.command("tagall") & filters.group)
async def tagall(client, msg: Message):
    # Command message delete karo
    try:
        await msg.delete()
    except Exception:
        pass

    if not msg.from_user:
        return await msg.reply_text("❌ Anonymous admin use nahi kar sakte.")

    uid     = msg.from_user.id
    chat_id = msg.chat.id

    if not await _is_admin(client, chat_id, uid):
        return await msg.reply_text("❌ <b>Sirf group admins /tagall use kar sakte hain!</b>")

    parts      = msg.text.split(maxsplit=1)
    custom_msg = parts[1].strip() if len(parts) > 1 else "📢 <b>Everyone!</b>"

    status = await client.send_message(chat_id, "⏳ <b>Members fetch ho rahe hain...</b>")

    members = []
    try:
        async for member in client.get_chat_members(chat_id):
            u = member.user
            if u and not u.is_bot and not u.is_deleted:
                members.append(u)
    except ChatAdminRequired:
        return await status.edit_text("❌ <b>Bot ko admin banana padega!</b>")
    except Exception as e:
        return await status.edit_text(f"❌ <b>Error:</b> <code>{e}</code>")

    if not members:
        return await status.edit_text("❌ <b>Koi member nahi mila!</b>")

    total = len(members)
    await status.edit_text(f"📢 <b>Tagging {total} members...</b>")

    for i in range(0, total, 5):
        chunk = members[i:i + 5]
        tags  = " ".join(
            f"<a href='tg://user?id={u.id}'>{u.first_name or 'User'}</a>"
            for u in chunk
        )
        text = f"{custom_msg}\n\n{tags}" if i == 0 else tags
        try:
            await client.send_message(chat_id, text, parse_mode=enums.ParseMode.HTML)
        except FloodWait as fw:
            await asyncio.sleep(fw.value + 2)
            try:
                await client.send_message(chat_id, text, parse_mode=enums.ParseMode.HTML)
            except Exception:
                pass
        except Exception:
            pass
        await asyncio.sleep(1)

    await status.edit_text(f"✅ <b>Done! {total} members tag ho gaye.</b>")
