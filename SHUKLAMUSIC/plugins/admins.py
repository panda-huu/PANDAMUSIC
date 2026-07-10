import asyncio
import time

from pyrogram import filters, enums
from pyrogram.types import CallbackQuery, Message

import config
from SHUKLAMUSIC import app
from SHUKLAMUSIC.core.call import SHUKLA
from SHUKLAMUSIC.misc import db
from SHUKLAMUSIC.helpers import (
    get_lang,
    is_active_chat,
    group_assistant,
    _start_time,
)
from strings import get_string

# ══════════════════════════════════════════════════════════
#  PROGRESS TRACKING  (imported by stream.py)
# ══════════════════════════════════════════════════════════

_progress_tasks: dict = {}

# ══════════════════════════════════════════════════════════
#  AUTH USERS STORAGE
#  { chat_id: { user_id: added_by_user_id } }
# ══════════════════════════════════════════════════════════
_auth_users: dict = {}


def _fmt(seconds: int) -> str:
    seconds = max(0, int(seconds))
    m, s = divmod(seconds, 60)
    return f"{m}:{s:02d}"


def _build_progress_bar(elapsed: int, total: int, width: int = 9) -> str:
    if total <= 0:
        return f"{_fmt(elapsed)} {'─'*width}● ∞"
    ratio = min(elapsed / total, 1.0)
    dot_pos = round(ratio * width)  # round instead of int so dot reaches end
    dot_pos = min(dot_pos, width)   # clamp to width max
    bar = "─" * dot_pos + "●" + "─" * (width - dot_pos)
    return f"{_fmt(elapsed)} {bar} {_fmt(total)}"


async def _progress_loop(chat_id: int):
    while True:
        await asyncio.sleep(8)
        try:
            if not db.get(chat_id):
                break
            start = _start_time.get(chat_id)
            if start is None:
                break
            elapsed = int(time.time() - start)
            total = db[chat_id][0].get("seconds", 0)
            db[chat_id][0]["played"] = elapsed

            # ── Live progress bar update in inline buttons ──
            try:
                mystic = db[chat_id][0].get("mystic")
                markup_type = db[chat_id][0].get("markup", "stream")
                if mystic and markup_type == "stream":
                    bar_text = _build_progress_bar(elapsed, total, width=9)
                    from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
                    new_markup = InlineKeyboardMarkup([
                        [
                            InlineKeyboardButton("⟨⟨", callback_data=f"ADMIN Replay|{chat_id}"),
                            InlineKeyboardButton("▷", callback_data=f"ADMIN Resume|{chat_id}"),
                            InlineKeyboardButton("II", callback_data=f"ADMIN Pause|{chat_id}"),
                            InlineKeyboardButton("‣‣I", callback_data=f"ADMIN Skip|{chat_id}"),
                            InlineKeyboardButton("▢", callback_data=f"ADMIN Stop|{chat_id}"),
                        ],
                        [
                            InlineKeyboardButton(bar_text, callback_data=f"ADMIN Progress|{chat_id}"),
                        ],
                        [
                            InlineKeyboardButton("« 10s", callback_data=f"ADMIN SeekBack|{chat_id}"),
                            InlineKeyboardButton("10s »", callback_data=f"ADMIN SeekFwd|{chat_id}"),
                        ],
                        [
                            InlineKeyboardButton("ᴏᴡɴᴇʀ", url=f"https://t.me/{config.OWNER_USERNAME}"),
                            InlineKeyboardButton("sᴜᴘᴘᴏʀᴛ", url=config.SUPPORT_CHANNEL),
                        ],
                        [
                            InlineKeyboardButton("✖ ᴄʟᴏsᴇ", callback_data=f"ADMIN ClosePanel|{chat_id}"),
                        ],
                    ])
                    await mystic.edit_reply_markup(reply_markup=new_markup)
            except Exception:
                pass  # Message edit fail ho toh silently ignore karo
            # ───────────────────────────────────────────────

            if total and elapsed >= total:
                break
        except Exception:
            break


def start_progress_task(chat_id: int):
    old = _progress_tasks.get(chat_id)
    if old and not old.done():
        old.cancel()
    task = asyncio.create_task(_progress_loop(chat_id))
    _progress_tasks[chat_id] = task


# ══════════════════════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════════════════════

def is_owner(user_id: int) -> bool:
    return user_id == config.OWNER_ID


async def _is_admin(client, chat_id: int, user_id: int) -> bool:
    try:
        member = await client.get_chat_member(chat_id, user_id)
        return member.status.value in ("administrator", "creator")
    except Exception:
        return False


def is_auth_user(chat_id: int, user_id: int) -> bool:
    """Returns True if user is in auth list for this chat."""
    return user_id in _auth_users.get(chat_id, {})


async def can_control(client, chat_id: int, user_id: int) -> bool:
    """Only owner or group admin can control player panel."""
    if is_owner(user_id):
        return True
    if await _is_admin(client, chat_id, user_id):
        return True
    return False


# ══════════════════════════════════════════════════════════
#  /auth  COMMAND
# ══════════════════════════════════════════════════════════

@app.on_message(
    filters.command(["auth"], prefixes=["/", "!", ".", ","]) & filters.group
)
async def auth_command(client, message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    # Only owner or group admin can auth someone
    if not (is_owner(user_id) or await _is_admin(client, chat_id, user_id)):
        return await message.reply_text("❖ Only owner or group admins can auth users.")

    target_id = None
    target_mention = None

    # Reply to a message
    if message.reply_to_message and message.reply_to_message.from_user:
        target_id = message.reply_to_message.from_user.id
        target_mention = message.reply_to_message.from_user.mention

    # /auth <user_id>
    elif len(message.command) > 1:
        try:
            target_id = int(message.command[1])
            user_obj = await client.get_users(target_id)
            target_mention = user_obj.mention
        except Exception:
            return await message.reply_text("❖ Invalid user id.")

    else:
        return await message.reply_text(
            "❖ Usage:\n`/auth <user_id>`\nor reply to a user's message with `/auth`"
        )

    # Don't auth owner (already has all perms)
    if target_id == config.OWNER_ID:
        return await message.reply_text("❖ Owner is already the supreme controller 👑")

    if chat_id not in _auth_users:
        _auth_users[chat_id] = {}

    if target_id in _auth_users[chat_id]:
        return await message.reply_text(f"❖ {target_mention} is already an authorized user.")

    if len(_auth_users[chat_id]) >= 25:
        return await message.reply_text("❖ Max 25 authorized users allowed per group.")

    _auth_users[chat_id][target_id] = user_id
    await message.reply_text(
        f"✅ **{target_mention}** has been added to authorized users.\n"
        f"They can now control the music player."
    )


# ══════════════════════════════════════════════════════════
#  /unauth  COMMAND
# ══════════════════════════════════════════════════════════

@app.on_message(
    filters.command(["unauth"], prefixes=["/", "!", ".", ","]) & filters.group
)
async def unauth_command(client, message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    if not (is_owner(user_id) or await _is_admin(client, chat_id, user_id)):
        return await message.reply_text("❖ Only owner or group admins can unauth users.")

    target_id = None
    target_mention = None

    if message.reply_to_message and message.reply_to_message.from_user:
        target_id = message.reply_to_message.from_user.id
        target_mention = message.reply_to_message.from_user.mention
    elif len(message.command) > 1:
        try:
            target_id = int(message.command[1])
            user_obj = await client.get_users(target_id)
            target_mention = user_obj.mention
        except Exception:
            return await message.reply_text("❖ Invalid user id.")
    else:
        return await message.reply_text(
            "❖ Usage:\n`/unauth <user_id>`\nor reply to a user's message with `/unauth`"
        )

    if target_id not in _auth_users.get(chat_id, {}):
        return await message.reply_text(f"❖ {target_mention} is not in authorized users list.")

    del _auth_users[chat_id][target_id]
    await message.reply_text(f"✅ **{target_mention}** removed from authorized users.")


# ══════════════════════════════════════════════════════════
#  /authusers  COMMAND
# ══════════════════════════════════════════════════════════

@app.on_message(
    filters.command(["authusers", "authed"], prefixes=["/", "!", ".", ","]) & filters.group
)
async def authusers_command(client, message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    if not (is_owner(user_id) or await _is_admin(client, chat_id, user_id)):
        return await message.reply_text("❖ Only owner or admins can view authorized users.")

    auth_dict = _auth_users.get(chat_id, {})
    if not auth_dict:
        return await message.reply_text("❖ No authorized users in this group.")

    text = f"**🔐 Authorized Users in {message.chat.title}:**\n\n"
    for uid in auth_dict:
        try:
            u = await client.get_users(uid)
            text += f"• {u.mention} (`{uid}`)\n"
        except Exception:
            text += f"• `{uid}`\n"

    await message.reply_text(text)


# ══════════════════════════════════════════════════════════
#  /skip COMMAND
# ══════════════════════════════════════════════════════════

@app.on_message(
    filters.command(["skip", "vskip"], prefixes=["/", "!", ".", ","]) & filters.group
)
async def skip_command(client, message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    try:
        language = await get_lang(chat_id)
        _ = get_string(language)
    except Exception:
        _ = get_string("en")

    # ✅ Permission check hatao — sab use kar sakte hain
    if not await is_active_chat(chat_id):
        return await message.reply_text("❖ No active stream found.")
    check = db.get(chat_id)
    if not check:
        return await message.reply_text("❖ Queue is empty.")
    if len(check) <= 1:
        await SHUKLA.stop_stream(chat_id)
        return await message.reply_text(
            _["admin_6"].format(message.from_user.mention, message.chat.title)
        )
    try:
        assistant = await group_assistant(SHUKLA, chat_id)
        await SHUKLA.change_stream(assistant, chat_id)
        await message.reply_text(
            _["admin_6"].format(message.from_user.mention, message.chat.title)
        )
    except Exception as e:
        await message.reply_text(f"❖ Failed to skip: {type(e).__name__}")


# ══════════════════════════════════════════════════════════
#  /stop COMMAND
# ══════════════════════════════════════════════════════════

@app.on_message(
    filters.command(["stop", "end"], prefixes=["/", "!", ".", ","]) & filters.group
)
async def stop_command(client, message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    try:
        language = await get_lang(chat_id)
        _ = get_string(language)
    except Exception:
        _ = get_string("en")

    # ✅ Permission check hatao — sab use kar sakte hain
    if not await is_active_chat(chat_id):
        return await message.reply_text("❖ No active stream found.")
    try:
        await SHUKLA.stop_stream(chat_id)
        await message.reply_text(_["admin_5"].format(message.from_user.mention))
    except Exception as e:
        await message.reply_text(f"❖ Failed to stop: {type(e).__name__}")


# ══════════════════════════════════════════════════════════
#  PLAYER PANEL BUTTON CALLBACKS
# ══════════════════════════════════════════════════════════

@app.on_callback_query(filters.regex("^ADMIN "))
async def admin_callback(client, CallbackQuery: CallbackQuery):
    try:
        callback_data = CallbackQuery.data.strip()
        _, action_chat = callback_data.split(None, 1)
        action, chat_id = action_chat.split("|")
        chat_id = int(chat_id)
        action = action.strip()
    except Exception:
        return await CallbackQuery.answer("Invalid data.", show_alert=True)

    try:
        language = await get_lang(chat_id)
        _ = get_string(language)
    except Exception:
        _ = get_string("en")

    user_id = CallbackQuery.from_user.id

    if not await can_control(client, chat_id, user_id):
        return await CallbackQuery.answer(
            "❖ Only admins or authorized users can control the player.",
            show_alert=True
        )
    if not await is_active_chat(chat_id):
        return await CallbackQuery.answer("❖ No active stream.", show_alert=True)

    # ── Resume ────────────────────────────────────────────
    if action == "Resume":
        try:
            await SHUKLA.resume_stream(chat_id)
            await CallbackQuery.answer(_["admin_1"], show_alert=True)
        except Exception as e:
            await CallbackQuery.answer(f"Error: {type(e).__name__}", show_alert=True)

    # ── Pause ─────────────────────────────────────────────
    elif action == "Pause":
        try:
            await SHUKLA.pause_stream(chat_id)
            await CallbackQuery.answer(_["admin_3"], show_alert=True)
        except Exception as e:
            await CallbackQuery.answer(f"Error: {type(e).__name__}", show_alert=True)

    # ── Skip ──────────────────────────────────────────────
    elif action == "Skip":
        check = db.get(chat_id)
        if not check or len(check) <= 1:
            await SHUKLA.stop_stream(chat_id)
            await CallbackQuery.answer(
                _["admin_6"].format(
                    CallbackQuery.from_user.mention,
                    CallbackQuery.message.chat.title or str(chat_id),
                ),
                show_alert=True,
            )
            try:
                await CallbackQuery.message.delete()
            except Exception:
                pass
        else:
            try:
                assistant = await group_assistant(SHUKLA, chat_id)
                await SHUKLA.change_stream(assistant, chat_id)
                await CallbackQuery.answer(
                    _["admin_6"].format(
                        CallbackQuery.from_user.mention,
                        CallbackQuery.message.chat.title or str(chat_id),
                    ),
                    show_alert=True,
                )
            except Exception as e:
                await CallbackQuery.answer(f"Error: {type(e).__name__}", show_alert=True)

    # ── Stop ──────────────────────────────────────────────
    elif action == "Stop":
        try:
            user = CallbackQuery.from_user
            user_mention = f'<a href="tg://user?id={user.id}">{user.first_name}</a>'
            await SHUKLA.stop_stream(chat_id)
            try:
                await CallbackQuery.message.delete()
            except Exception:
                pass
            await app.send_message(
                chat_id,
                f"🛑 <b>sᴛʀᴇᴀᴍɪɴɢ sᴛᴏᴘᴘᴇᴅ ʙʏ</b> {user_mention}",
                parse_mode=enums.ParseMode.HTML,
            )
        except Exception as e:
            await CallbackQuery.answer(f"Error: {type(e).__name__}", show_alert=True)

    # ── Replay ────────────────────────────────────────────
    elif action == "Replay":
        try:
            check = db.get(chat_id)
            if not check:
                return await CallbackQuery.answer("Nothing playing.", show_alert=True)
            playing = check[0]
            file_path = playing.get("file")
            video = True if playing.get("streamtype") == "video" else False
            if file_path and "vid_" in str(file_path):
                from SHUKLAMUSIC import YouTube
                mystic = await CallbackQuery.message.reply_text("⏮ Replaying...")
                vidid = playing.get("vidid")
                file_path, direct = await YouTube.download(
                    vidid, mystic, videoid=True, video=video
                )
                await mystic.delete()
            await SHUKLA.skip_stream(chat_id, file_path, video=video)
            db[chat_id][0]["played"] = 0
            _start_time[chat_id] = time.time()
            start_progress_task(chat_id)
            await CallbackQuery.answer("⏮ Replaying from start!", show_alert=True)
        except Exception as e:
            await CallbackQuery.answer(f"Error: {type(e).__name__}", show_alert=True)

    # ── Progress Bar ──────────────────────────────────────
    elif action == "Progress":
        try:
            check = db.get(chat_id)
            if not check:
                return await CallbackQuery.answer("Nothing playing.", show_alert=True)
            playing = check[0]
            title = playing.get("title", "Unknown")[:20]
            total = playing.get("seconds", 0)
            start = _start_time.get(chat_id)
            elapsed = int(time.time() - start) if start else playing.get("played", 0)
            elapsed = min(elapsed, total) if total else elapsed

            m1, s1 = divmod(max(0, elapsed), 60)
            m2, s2 = divmod(max(0, total), 60)
            t_elapsed = f"{m1}:{s1:02d}"
            t_total = f"{m2}:{s2:02d}"

            if total > 0:
                pct = int(min(elapsed / total, 1.0) * 10)
                bar = "█" * pct + "─" * (10 - pct)
            else:
                bar = "──────────"

            line1 = title
            line2 = f"{t_elapsed} {bar} {t_total}"
            await CallbackQuery.answer(f"{line1}\n{line2}", show_alert=True)
        except Exception as e:
            import traceback
            tb = traceback.format_exc()
            short = tb.split("\n")[-3] if tb else str(e)
            await CallbackQuery.answer(f"ERR: {short[:180]}", show_alert=True)

    # ── SeekBack 10s ─────────────────────────────────────
    elif action == "SeekBack":
        try:
            check = db.get(chat_id)
            if not check:
                return await CallbackQuery.answer("Nothing playing.", show_alert=True)
            playing = check[0]
            file_path = playing.get("file")
            total = playing.get("seconds", 0)
            mode = playing.get("streamtype", "audio")

            # Calculate current elapsed
            start = _start_time.get(chat_id)
            elapsed = int(time.time() - start) if start else playing.get("played", 0)
            new_pos = max(0, elapsed - 10)

            if not file_path or "vid_" in str(file_path) or total == 0:
                return await CallbackQuery.answer(
                    "⏪ Seek not supported for this stream.", show_alert=True
                )

            # Format: MM:SS for ffmpeg -ss and -to
            def _ts(s):
                s = max(0, int(s))
                m, sec = divmod(s, 60)
                return f"{m:02d}:{sec:02d}"

            await SHUKLA.seek_stream(
                chat_id,
                file_path,
                to_seek=_ts(new_pos),
                duration=_ts(total),
                mode=mode,
            )
            # Update start_time so progress bar stays accurate
            _start_time[chat_id] = time.time() - new_pos
            db[chat_id][0]["played"] = new_pos
            await CallbackQuery.answer(f"⏪ Seeked to {_ts(new_pos)}", show_alert=True)
        except Exception as e:
            await CallbackQuery.answer(f"Error: {type(e).__name__}", show_alert=True)

    # ── SeekFwd 10s ──────────────────────────────────────
    elif action == "SeekFwd":
        try:
            check = db.get(chat_id)
            if not check:
                return await CallbackQuery.answer("Nothing playing.", show_alert=True)
            playing = check[0]
            file_path = playing.get("file")
            total = playing.get("seconds", 0)
            mode = playing.get("streamtype", "audio")

            # Calculate current elapsed
            start = _start_time.get(chat_id)
            elapsed = int(time.time() - start) if start else playing.get("played", 0)
            new_pos = elapsed + 10
            if total and new_pos >= total:
                return await CallbackQuery.answer(
                    "⏩ Can't seek beyond song end.", show_alert=True
                )

            if not file_path or "vid_" in str(file_path) or total == 0:
                return await CallbackQuery.answer(
                    "⏩ Seek not supported for this stream.", show_alert=True
                )

            def _ts(s):
                s = max(0, int(s))
                m, sec = divmod(s, 60)
                return f"{m:02d}:{sec:02d}"

            await SHUKLA.seek_stream(
                chat_id,
                file_path,
                to_seek=_ts(new_pos),
                duration=_ts(total),
                mode=mode,
            )
            # Update start_time so progress bar stays accurate
            _start_time[chat_id] = time.time() - new_pos
            db[chat_id][0]["played"] = new_pos
            await CallbackQuery.answer(f"⏩ Seeked to {_ts(new_pos)}", show_alert=True)
        except Exception as e:
            await CallbackQuery.answer(f"Error: {type(e).__name__}", show_alert=True)

    # ── ClosePanel ────────────────────────────────────────
    elif action == "ClosePanel":
        try:
            await CallbackQuery.message.delete()
        except Exception:
            await CallbackQuery.answer("Panel delete nahi hua.", show_alert=True)

    else:
        await CallbackQuery.answer("Unknown action.", show_alert=True)
