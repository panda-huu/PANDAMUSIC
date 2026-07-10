import asyncio

from pyrogram import enums, filters
from pyrogram.errors import (
    FloodWait,
    InputUserDeactivated,
    PeerIdInvalid,
    UserIsBlocked,
    ChatWriteForbidden,
    ChannelPrivate,
)
from pyrogram.types import Message

import config
from SHUKLAMUSIC import app
from config import BANNED_USERS
from SHUKLAMUSIC.helpers import get_served_users, get_served_chats


# ── Helper: send one message (forward or copy) ────────────────────────────────

async def _send_broadcast(chat_id: int, msg: Message) -> bool:
    try:
        await msg.forward(chat_id)
        return True
    except FloodWait as fw:
        await asyncio.sleep(fw.value + 1)
        try:
            await msg.forward(chat_id)
            return True
        except Exception:
            return False
    except (
        UserIsBlocked,
        InputUserDeactivated,
        PeerIdInvalid,
        ChatWriteForbidden,
        ChannelPrivate,
    ):
        return False
    except Exception:
        return False


# ── /broadcast — to all USERS ─────────────────────────────────────────────────

@app.on_message(
    filters.command(["broadcast", "bc"])
    & filters.user(
        list(config.OWNER_ID)
        if isinstance(config.OWNER_ID, (list, set))
        else [config.OWNER_ID]
    )
)
async def broadcast_users(client, message: Message):
    if not message.reply_to_message:
        m = await message.reply_text(
            "📢 <b>ʙʀᴏᴀᴅᴄᴀsᴛ</b>\n\n"
            "ʀᴇᴘʟʏ ᴛᴏ ᴀɴʏ ᴍᴇssᴀɢᴇ ʙʀᴏᴀᴅᴄᴀsᴛ ᴛᴏ ᴜsᴇʀs.\n\n"
            "<b>Usage:</b>\n"
            "/broadcast — sab users ko\n"
            "/gbroadcast — sab groups ko\n"
            "/abroadcast — users + groups dono ko",
            parse_mode=enums.ParseMode.HTML,
        )
        await asyncio.sleep(10)
        try: await message.delete()
        except: pass
        try: await m.delete()
        except: pass
        return

    broadcast_msg = message.reply_to_message
    users = await get_served_users()

    try: await message.delete()
    except: pass

    status = await broadcast_msg.reply_text(
        f"📢 <b>ʙʀᴏᴀᴅᴄᴀsᴛ sᴛᴀʀᴛᴇᴅ</b>\n\n"
        f"• <b>ᴛᴀʀɢᴇᴛ:</b> {len(users)} ᴜsᴇʀs\n"
        f"• <b>sᴛᴀᴛᴜs:</b> ᴘʀᴏᴄᴇssɪɴɢ...",
        parse_mode=enums.ParseMode.HTML,
    )

    done = 0
    failed = 0

    for user in users:
        uid = user.get("user_id")
        if not uid:
            continue
        success = await _send_broadcast(uid, broadcast_msg)
        if success:
            done += 1
        else:
            failed += 1
        await asyncio.sleep(0.05)

    await status.edit_text(
        f"✅ <b>ʙʀᴏᴀᴅᴄᴀsᴛ ᴄᴏᴍᴘʟᴇᴛᴇ</b>\n\n"
        f"• <b>ᴛᴏᴛᴀʟ:</b> {len(users)}\n"
        f"• <b>sᴜᴄᴄᴇss:</b> {done}\n"
        f"• <b>ғᴀɪʟᴇᴅ:</b> {failed}",
        parse_mode=enums.ParseMode.HTML,
    )
    await asyncio.sleep(30)
    try: await status.delete()
    except: pass


# ── /gbroadcast — to all GROUPS ───────────────────────────────────────────────

@app.on_message(
    filters.command(["gbroadcast", "gbc"])
    & filters.user(
        list(config.OWNER_ID)
        if isinstance(config.OWNER_ID, (list, set))
        else [config.OWNER_ID]
    )
)
async def broadcast_groups(client, message: Message):
    if not message.reply_to_message:
        m = await message.reply_text(
            "📢 ʀᴇᴘʟʏ ᴛᴏ ᴀɴʏ ᴍᴇssᴀɢᴇ ʙʀᴏᴀᴅᴄᴀsᴛ ᴛᴏ ɢʀᴏᴜᴘ.",
            parse_mode=enums.ParseMode.HTML,
        )
        await asyncio.sleep(10)
        try: await message.delete()
        except: pass
        try: await m.delete()
        except: pass
        return

    broadcast_msg = message.reply_to_message
    chats = await get_served_chats()

    try: await message.delete()
    except: pass

    status = await broadcast_msg.reply_text(
        f"📢 <b>ɢʀᴏᴜᴘ ʙʀᴏᴀᴅᴄᴀsᴛ sᴛᴀʀᴛᴇᴅ</b>\n\n"
        f"• <b>ᴛᴀʀɢᴇᴛ:</b> {len(chats)} ɢʀᴏᴜᴘs\n"
        f"• <b>sᴛᴀᴛᴜs:</b> ᴘʀᴏᴄᴇssɪɴɢ...",
        parse_mode=enums.ParseMode.HTML,
    )

    done = 0
    failed = 0

    for chat in chats:
        cid = chat.get("chat_id")
        if not cid:
            continue
        success = await _send_broadcast(cid, broadcast_msg)
        if success:
            done += 1
        else:
            failed += 1
        await asyncio.sleep(0.05)

    await status.edit_text(
        f"✅ <b>ɢʀᴏᴜᴘ ʙʀᴏᴀᴅᴄᴀsᴛ ᴄᴏᴍᴘʟᴇᴛᴇ</b>\n\n"
        f"• <b>ᴛᴏᴛᴀʟ:</b> {len(chats)}\n"
        f"• <b>sᴜᴄᴄᴇss:</b> {done}\n"
        f"• <b>ғᴀɪʟᴇᴅ:</b> {failed}",
        parse_mode=enums.ParseMode.HTML,
    )
    await asyncio.sleep(30)
    try: await status.delete()
    except: pass


# ── /abroadcast — to USERS + GROUPS both ──────────────────────────────────────

@app.on_message(
    filters.command(["abroadcast", "abc"])
    & filters.user(
        list(config.OWNER_ID)
        if isinstance(config.OWNER_ID, (list, set))
        else [config.OWNER_ID]
    )
)
async def broadcast_all(client, message: Message):
    if not message.reply_to_message:
        m = await message.reply_text(
            "📢 ʀᴇᴘʟʏ ᴛᴏ ᴀɴʏ ᴍᴇssᴀɢᴇ ᴛᴏ ʙʀᴏᴀᴅᴄᴀsᴛ ᴛᴏ ᴜsᴇʀ+ɢʀᴏᴜᴘ.",
            parse_mode=enums.ParseMode.HTML,
        )
        await asyncio.sleep(10)
        try: await message.delete()
        except: pass
        try: await m.delete()
        except: pass
        return

    broadcast_msg = message.reply_to_message
    users = await get_served_users()
    chats = await get_served_chats()
    total = len(users) + len(chats)

    try: await message.delete()
    except: pass

    status = await broadcast_msg.reply_text(
        f"📢 <b>ғᴜʟʟ ʙʀᴏᴀᴅᴄᴀsᴛ sᴛᴀʀᴛᴇᴅ</b>\n\n"
        f"• <b>ᴜsᴇʀs:</b> {len(users)}\n"
        f"• <b>ɢʀᴏᴜᴘs:</b> {len(chats)}\n"
        f"• <b>ᴛᴏᴛᴀʟ:</b> {total}\n"
        f"• <b>sᴛᴀᴛᴜs:</b> ᴘʀᴏᴄᴇssɪɴɢ...",
        parse_mode=enums.ParseMode.HTML,
    )

    done = 0
    failed = 0

    for user in users:
        uid = user.get("user_id")
        if not uid:
            continue
        success = await _send_broadcast(uid, broadcast_msg)
        if success:
            done += 1
        else:
            failed += 1
        await asyncio.sleep(0.05)

    for chat in chats:
        cid = chat.get("chat_id")
        if not cid:
            continue
        success = await _send_broadcast(cid, broadcast_msg)
        if success:
            done += 1
        else:
            failed += 1
        await asyncio.sleep(0.05)

    await status.edit_text(
        f"✅ <b>ғᴜʟʟ ʙʀᴏᴀᴅᴄᴀsᴛ ᴄᴏᴍᴘʟᴇᴛᴇ</b>\n\n"
        f"• <b>ᴛᴏᴛᴀʟ:</b> {total}\n"
        f"• <b>sᴜᴄᴄᴇss:</b> {done}\n"
        f"• <b>ғᴀɪʟᴇᴅ:</b> {failed}",
        parse_mode=enums.ParseMode.HTML,
    )
    await asyncio.sleep(30)
    try: await status.delete()
    except: pass
