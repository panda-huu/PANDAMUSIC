# ---------------------------------------------------------------
# 🔸 RADHExMUSIC — moderation.py
# 🔹 Admin cmds: mute, unmute, ban, unban, kick (with reason)
# ---------------------------------------------------------------

from pyrogram import filters, enums
from pyrogram.errors import ChatAdminRequired, UserAdminInvalid
from pyrogram.types import Message, ChatPermissions

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


async def _get_target_and_reason(msg: Message):
    target = None
    reason = None
    if msg.reply_to_message and msg.reply_to_message.from_user:
        target = msg.reply_to_message.from_user
        parts  = msg.text.split(None, 1)
        reason = parts[1].strip() if len(parts) > 1 else None
    elif len(msg.command) > 1:
        try:
            target = await msg._client.get_users(msg.command[1])
            parts  = msg.text.split(None, 2)
            reason = parts[2].strip() if len(parts) > 2 else None
        except Exception:
            return None, None
    return target, reason


def _tag(user):
    return f"<a href='tg://user?id={user.id}'>{user.first_name or 'User'}</a>"


def _reason_line(reason):
    return f"\n📋 <b>ʀᴇᴀsᴏɴ:</b> {reason}" if reason else ""


# ── MUTE ─────────────────────────────────────────────────────

@app.on_message(filters.command("mute") & filters.group)
async def mute_user(client, msg: Message):
    try:
        await msg.delete()
    except Exception:
        pass
    if not msg.from_user:
        return
    if not await _is_admin(client, msg.chat.id, msg.from_user.id):
        return await msg.reply_text("❌ <b>ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴍᴜᴛᴇ!</b>")

    target, reason = await _get_target_and_reason(msg)
    if not target:
        return await msg.reply_text(
            "❌ <b>ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ ᴏʀ ᴘʀᴏᴠɪᴅᴇ ᴜsᴇʀɴᴀᴍᴇ/ɪᴅ!</b>\n"
            "<code>/mute @user reason</code>"
        )
    if target.id == msg.from_user.id:
        return await msg.reply_text("❌ <b>ʏᴏᴜ ᴄᴀɴɴᴏᴛ ᴍᴜᴛᴇ ʏᴏᴜʀsᴇʟꜰ!</b>")

    try:
        await client.restrict_chat_member(
            msg.chat.id, target.id,
            ChatPermissions(
                can_send_messages=False,
                can_send_media_messages=False,
                can_add_web_page_previews=False,
            ),
        )
        await client.send_message(
            msg.chat.id,
            f"🔇 <b>{_tag(target)} ʜᴀs ʙᴇᴇɴ ᴍᴜᴛᴇᴅ!</b>\n"
            f"👮 <b>ʙʏ:</b> {_tag(msg.from_user)}"
            f"{_reason_line(reason)}",
            reply_to_message_id=msg.reply_to_message.id if msg.reply_to_message else None,
        )
    except ChatAdminRequired:
        await msg.reply_text("❌ <b>ʙᴏᴛ ᴍᴜsᴛ ʙᴇ ᴀᴅᴍɪɴ!</b>")
    except UserAdminInvalid:
        await msg.reply_text("❌ <b>ᴄᴀɴɴᴏᴛ ᴍᴜᴛᴇ ᴀɴ ᴀᴅᴍɪɴ!</b>")
    except Exception as e:
        await msg.reply_text(f"❌ <b>ᴇʀʀᴏʀ:</b> <code>{e}</code>")


# ── UNMUTE ───────────────────────────────────────────────────

@app.on_message(filters.command("unmute") & filters.group)
async def unmute_user(client, msg: Message):
    try:
        await msg.delete()
    except Exception:
        pass
    if not msg.from_user:
        return
    if not await _is_admin(client, msg.chat.id, msg.from_user.id):
        return await msg.reply_text("❌ <b>ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜɴᴍᴜᴛᴇ!</b>")

    target, reason = await _get_target_and_reason(msg)
    if not target:
        return await msg.reply_text(
            "❌ <b>ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ ᴏʀ ᴘʀᴏᴠɪᴅᴇ ᴜsᴇʀɴᴀᴍᴇ/ɪᴅ!</b>\n"
            "<code>/unmute @user reason</code>"
        )

    try:
        await client.restrict_chat_member(
            msg.chat.id, target.id,
            ChatPermissions(
                can_send_messages=True,
                can_send_media_messages=True,
                can_add_web_page_previews=True,
            ),
        )
        await client.send_message(
            msg.chat.id,
            f"🔊 <b>{_tag(target)} ʜᴀs ʙᴇᴇɴ ᴜɴᴍᴜᴛᴇᴅ!</b>\n"
            f"👮 <b>ʙʏ:</b> {_tag(msg.from_user)}"
            f"{_reason_line(reason)}",
            reply_to_message_id=msg.reply_to_message.id if msg.reply_to_message else None,
        )
    except ChatAdminRequired:
        await msg.reply_text("❌ <b>ʙᴏᴛ ᴍᴜsᴛ ʙᴇ ᴀᴅᴍɪɴ!</b>")
    except Exception as e:
        await msg.reply_text(f"❌ <b>ᴇʀʀᴏʀ:</b> <code>{e}</code>")


# ── BAN ──────────────────────────────────────────────────────

@app.on_message(filters.command("ban") & filters.group)
async def ban_user(client, msg: Message):
    try:
        await msg.delete()
    except Exception:
        pass
    if not msg.from_user:
        return
    if not await _is_admin(client, msg.chat.id, msg.from_user.id):
        return await msg.reply_text("❌ <b>ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ʙᴀɴ!</b>")

    target, reason = await _get_target_and_reason(msg)
    if not target:
        return await msg.reply_text(
            "❌ <b>ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ ᴏʀ ᴘʀᴏᴠɪᴅᴇ ᴜsᴇʀɴᴀᴍᴇ/ɪᴅ!</b>\n"
            "<code>/ban @user reason</code>"
        )
    if target.id == msg.from_user.id:
        return await msg.reply_text("❌ <b>ʏᴏᴜ ᴄᴀɴɴᴏᴛ ʙᴀɴ ʏᴏᴜʀsᴇʟꜰ!</b>")

    try:
        await client.ban_chat_member(msg.chat.id, target.id)
        await client.send_message(
            msg.chat.id,
            f"🚫 <b>{_tag(target)} ʜᴀs ʙᴇᴇɴ ʙᴀɴɴᴇᴅ!</b>\n"
            f"👮 <b>ʙʏ:</b> {_tag(msg.from_user)}"
            f"{_reason_line(reason)}",
            reply_to_message_id=msg.reply_to_message.id if msg.reply_to_message else None,
        )
    except ChatAdminRequired:
        await msg.reply_text("❌ <b>ʙᴏᴛ ᴍᴜsᴛ ʙᴇ ᴀᴅᴍɪɴ!</b>")
    except UserAdminInvalid:
        await msg.reply_text("❌ <b>ᴄᴀɴɴᴏᴛ ʙᴀɴ ᴀɴ ᴀᴅᴍɪɴ!</b>")
    except Exception as e:
        await msg.reply_text(f"❌ <b>ᴇʀʀᴏʀ:</b> <code>{e}</code>")


# ── UNBAN ────────────────────────────────────────────────────

@app.on_message(filters.command("unban") & filters.group)
async def unban_user(client, msg: Message):
    try:
        await msg.delete()
    except Exception:
        pass
    if not msg.from_user:
        return
    if not await _is_admin(client, msg.chat.id, msg.from_user.id):
        return await msg.reply_text("❌ <b>ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜɴʙᴀɴ!</b>")

    target, reason = await _get_target_and_reason(msg)
    if not target:
        return await msg.reply_text(
            "❌ <b>ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ ᴏʀ ᴘʀᴏᴠɪᴅᴇ ᴜsᴇʀɴᴀᴍᴇ/ɪᴅ!</b>\n"
            "<code>/unban @user reason</code>"
        )

    try:
        await client.unban_chat_member(msg.chat.id, target.id)
        await client.send_message(
            msg.chat.id,
            f"✅ <b>{_tag(target)} ʜᴀs ʙᴇᴇɴ ᴜɴʙᴀɴɴᴇᴅ!</b>\n"
            f"👮 <b>ʙʏ:</b> {_tag(msg.from_user)}"
            f"{_reason_line(reason)}",
        )
    except ChatAdminRequired:
        await msg.reply_text("❌ <b>ʙᴏᴛ ᴍᴜsᴛ ʙᴇ ᴀᴅᴍɪɴ!</b>")
    except Exception as e:
        await msg.reply_text(f"❌ <b>ᴇʀʀᴏʀ:</b> <code>{e}</code>")


# ── KICK ─────────────────────────────────────────────────────

@app.on_message(filters.command("kick") & filters.group)
async def kick_user(client, msg: Message):
    try:
        await msg.delete()
    except Exception:
        pass
    if not msg.from_user:
        return
    if not await _is_admin(client, msg.chat.id, msg.from_user.id):
        return await msg.reply_text("❌ <b>ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴋɪᴄᴋ!</b>")

    target, reason = await _get_target_and_reason(msg)
    if not target:
        return await msg.reply_text(
            "❌ <b>ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ ᴏʀ ᴘʀᴏᴠɪᴅᴇ ᴜsᴇʀɴᴀᴍᴇ/ɪᴅ!</b>\n"
            "<code>/kick @user reason</code>"
        )
    if target.id == msg.from_user.id:
        return await msg.reply_text("❌ <b>ʏᴏᴜ ᴄᴀɴɴᴏᴛ ᴋɪᴄᴋ ʏᴏᴜʀsᴇʟꜰ!</b>")

    try:
        await client.ban_chat_member(msg.chat.id, target.id)
        await client.unban_chat_member(msg.chat.id, target.id)
        await client.send_message(
            msg.chat.id,
            f"👟 <b>{_tag(target)} ʜᴀs ʙᴇᴇɴ ᴋɪᴄᴋᴇᴅ!</b>\n"
            f"👮 <b>ʙʏ:</b> {_tag(msg.from_user)}"
            f"{_reason_line(reason)}",
            reply_to_message_id=msg.reply_to_message.id if msg.reply_to_message else None,
        )
    except ChatAdminRequired:
        await msg.reply_text("❌ <b>ʙᴏᴛ ᴍᴜsᴛ ʙᴇ ᴀᴅᴍɪɴ!</b>")
    except UserAdminInvalid:
        await msg.reply_text("❌ <b>ᴄᴀɴɴᴏᴛ ᴋɪᴄᴋ ᴀɴ ᴀᴅᴍɪɴ!</b>")
    except Exception as e:
        await msg.reply_text(f"❌ <b>ᴇʀʀᴏʀ:</b> <code>{e}</code>")
