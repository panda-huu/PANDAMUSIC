"""
SHUKLAMUSIC/plugins/botkick.py
Bot ko jab kisi group se kick/remove kiya jaaye to LOGGER_ID group me
log message bhejta hai (kisne kick kiya, kis group se, etc).
"""
from pyrogram import enums, filters
from pyrogram.types import ChatMemberUpdated
from pyrogram.enums import ParseMode

import config
from SHUKLAMUSIC import app


@app.on_chat_member_updated(filters.group)
async def bot_kick_logger(client, update: ChatMemberUpdated):
    try:
        new = update.new_chat_member
        old = update.old_chat_member

        # Sirf bot (khud) ke status change pe react karo
        target_user = (new.user if new else None) or (old.user if old else None)
        if target_user is None or not target_user.is_self:
            return

        # Naya status BANNED/KICKED ya LEFT hona chahiye
        if new is None or new.status not in (
            enums.ChatMemberStatus.BANNED,
            enums.ChatMemberStatus.LEFT,
        ):
            return

        # Pehle se hi LEFT/BANNED tha to skip (duplicate update na ho)
        if old and old.status in (
            enums.ChatMemberStatus.BANNED,
            enums.ChatMemberStatus.LEFT,
        ):
            return

        chat_id    = update.chat.id
        chat_title = update.chat.title or "Unknown Group"

        kicked_by = update.from_user  # jisne action kiya
        if kicked_by:
            kicker_name = kicked_by.first_name or "Unknown"
            kicker_id   = kicked_by.id
            kicker_link = f"<a href='tg://user?id={kicker_id}'>{kicker_name}</a>"
        else:
            kicker_link = "Unknown"
            kicker_id   = "N/A"

        action = "Kicked / Removed" if new.status == enums.ChatMemberStatus.BANNED else "Bot Left"

        text = (
            f"⚠️ <b>Bot {action} From Group</b>\n\n"
            f"🏠 <b>Group Name</b> ➤ {chat_title}\n"
            f"🆔 <b>Group ID</b> ➤ <code>{chat_id}</code>\n"
            f"👤 <b>Action By</b> ➤ {kicker_link}\n"
            f"🆔 <b>User ID</b> ➤ <code>{kicker_id}</code>\n"
        )

        await client.send_message(
            config.LOGGER_ID, text, parse_mode=ParseMode.HTML
        )
    except Exception:
        pass
