import asyncio
import random, time
from pyrogram import filters, enums
from pyrogram.enums import ChatType
from pyrogram import filters, enums, ContinuePropagation   # ← ContinuePropagation add kiya
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from py_yt import VideosSearch
import config
from SHUKLAMUSIC import app
from SHUKLAMUSIC.misc import _boot_, SUDOERS
from SHUKLAMUSIC.helpers import (
    LanguageStart, add_served_user, add_served_chat, get_served_chats,
    get_served_users, bot_sys_stats, get_readable_time, start_panel,
    private_panel, is_on_off, is_banned_user, blacklisted_chats,
    get_lang, get_string,
)
from config import BANNED_USERS, SHASHANK_IMG

@app.on_message(filters.command("start") & ~BANNED_USERS)
@LanguageStart
async def start_pm(client, message: Message, _):
    try:
        await message.delete()
    except Exception:
        pass
    await add_served_user(message.from_user.id)
    # ── Intro animation ──
    try:
        bot_name = (await client.get_me()).first_name
        anim = await client.send_message(message.chat.id, "ʀᴀᴅʜᴇ ʀᴀᴅʜᴇ 😁!")
        await asyncio.sleep(1)
        await anim.edit_text("ʜᴏᴡ ᴀʀᴇ ʏᴏᴜ")
        await asyncio.sleep(1)
        await anim.edit_text(f"ɪ ᴀᴍ {bot_name}")
        await asyncio.sleep(1)
        await anim.edit_text(f"{bot_name} sᴛᴀʀᴛɪɴɢ....")
        await asyncio.sleep(1)
        await anim.delete()
    except Exception:
        pass
    # Log to LOGGER group
    try:
        u = message.from_user
        ulink = f'<a href="tg://user?id={u.id}">{u.first_name}</a>'
        await app.send_message(
            config.LOGGER_ID,
            f"👤 <b>ɴᴇᴡ ᴜsᴇʀ sᴛᴀʀᴛᴇᴅ ʙᴏᴛ</b>\n"
            f"• <b>ɴᴀᴍᴇ:</b> {ulink}\n"
            f"• <b>ᴜ_ɴᴀᴍᴇ:</b> @{u.username or 'N/A'}\n"
            f"• <b>ᴜ_ɪᴅ:</b> <code>{u.id}</code>",
        )
    except Exception:
        pass
    if len(message.text.split()) > 1:
        name = message.text.split(None, 1)[1]
        if name.startswith("inf"):
            video_id = name.replace("info_", "", 1)
            yt_url = f"https://www.youtube.com/watch?v={video_id}"
            try:
                import yt_dlp
                ydl_opts = {"quiet": True, "skip_download": True, "noplaylist": True}
                loop = __import__("asyncio").get_event_loop()
                def _fetch():
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        return ydl.extract_info(yt_url, download=False)
                info = await loop.run_in_executor(None, _fetch)
                title = info.get("title", "Unknown")
                duration_sec = info.get("duration", 0)
                m, s = divmod(int(duration_sec), 60)
                duration = f"{m}:{s:02d}"
                views = f"{info.get('view_count', 0):,}"
                published = info.get("upload_date", "")
                if len(published) == 8:
                    published = f"{published[6:]}/{published[4:6]}/{published[:4]}"
                channel = info.get("uploader", "Unknown")
                channellink = info.get("uploader_url", yt_url)
                link = yt_url
                # Best quality thumbnail
                thumbs = info.get("thumbnails", [])
                thumbnail = thumbs[-1]["url"] if thumbs else f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg"
            except Exception:
                # Fallback to search
                results = VideosSearch(video_id, limit=1)
                for r in (await results.next())["result"]:
                    title = r["title"]; duration = r["duration"]
                    views = r["viewCount"]["short"]
                    thumbnail = r["thumbnails"][0]["url"].split("?")[0]
                    channellink = r["channel"]["link"]; channel = r["channel"]["name"]
                    link = r["link"]; published = r["publishedTime"]
            searched_text = _["start_6"].format(title, duration, views, published, channellink, channel, f"@{config.BOT_USERNAME}")
            key = InlineKeyboardMarkup([[
                InlineKeyboardButton(_["S_B_8"], url=link),
                InlineKeyboardButton(_["S_B_9"], url=config.SUPPORT_CHAT),
            ]])
            await app.send_photo(message.chat.id, photo=thumbnail, caption=searched_text, reply_markup=key)
        else:
            out = private_panel(_)
            served_chats = len(await get_served_chats())
            served_users = len(await get_served_users())
            UP, CPU, RAM, DISK = await bot_sys_stats()
            await message.reply_photo(
                random.choice(SHASHANK_IMG),
                caption=_["start_2"].format(message.from_user.mention, f"@{config.BOT_USERNAME}", UP, DISK, CPU, RAM, served_users, served_chats),
                reply_markup=InlineKeyboardMarkup(out),
            )
    else:
        out = private_panel(_)
        served_chats = len(await get_served_chats())
        served_users = len(await get_served_users())
        UP, CPU, RAM, DISK = await bot_sys_stats()
        await message.reply_photo(
            random.choice(SHASHANK_IMG),
            caption=_["start_2"].format(message.from_user.mention, f"@{config.BOT_USERNAME}", UP, DISK, CPU, RAM, served_users, served_chats),
            reply_markup=InlineKeyboardMarkup(out),
        )

@app.on_message(filters.command("start") & filters.group & ~BANNED_USERS)
@LanguageStart
async def start_gp(client, message: Message, _):
    await add_served_chat(message.chat.id)
    # ── Intro animation ──
    try:
        bot_name = (await client.get_me()).first_name
        anim = await message.reply_text("ʀᴀᴅʜᴇ ʀᴀᴅʜᴇ 😁!")
        await asyncio.sleep(1)
        await anim.edit_text("ʜᴏᴡ ᴀʀᴇ ʏᴏᴜ")
        await asyncio.sleep(1)
        await anim.edit_text(f"ɪ ᴀᴍ {bot_name}")
        await asyncio.sleep(1)
        await anim.edit_text(f"{bot_name} sᴛᴀʀᴛɪɴɢ....")
        await asyncio.sleep(1)
        await anim.delete()
    except Exception:
        pass
    served_chats = len(await get_served_chats())
    served_users = len(await get_served_users())
    UP, CPU, RAM, DISK = await bot_sys_stats()
    out = private_panel(_)
    await message.reply_photo(
        random.choice(SHASHANK_IMG),
        caption=_["start_2"].format(
            message.from_user.mention, f"@{config.BOT_USERNAME}",
            UP, DISK, CPU, RAM, served_users, served_chats
        ),
        reply_markup=InlineKeyboardMarkup(out),
    )

@app.on_message(filters.new_chat_members, group=-1)
async def welcome(client, message: Message):
    try:
        for member in message.new_chat_members:
            if member.id == client.me.id:
                try:
                    chat  = message.chat
                    adder = message.from_user
                    raw_id      = str(chat.id).replace("-", "")
                    chat_id_fmt = f"-100{raw_id}"
                    adder_link = (
                        f'<a href="tg://user?id={adder.id}">{adder.first_name}</a>'
                        if adder else "Unknown"
                    )
                    adder_un  = f"@{adder.username}" if adder and adder.username else "N/A"
                    adder_id  = adder.id if adder else "N/A"
                    total_chats = len(await get_served_chats())
                    await app.send_message(
                        config.LOGGER_ID,
                        f"➕ <b>ʙᴏᴛ ᴀᴅᴅᴇᴅ ᴛᴏ ɴᴇᴡ ɢʀᴏᴜᴘ</b>\n\n"
                        f"🏘 <b>ɢʀᴏᴜᴘ:</b> {chat.title}\n"
                        f"🆔 <b>ᴄʜᴀᴛ ɪᴅ:</b> <code>{chat_id_fmt}</code>\n"
                        f"👤 <b>ᴀᴅᴅᴇᴅ ʙʏ:</b> {adder_link}\n"
                        f"📛 <b>ᴜ_ɴᴀᴍᴇ:</b> {adder_un}\n"
                        f"🔢 <b>ᴜ_ɪᴅ:</b> <code>{adder_id}</code>\n"
                        f"📊 <b>ᴛᴏᴛᴀʟ ɢʀᴏᴜᴘs:</b> {total_chats}",
                        parse_mode=enums.ParseMode.HTML,
                    )
                except Exception as log_err:
                    print(f"[LOGGER ERROR] {log_err}")
    finally:
        raise ContinuePropagation   # ← CRITICAL: isके bina welcome.py kabhi nahi chalega

        try:
            _ = get_string(await get_lang(message.chat.id))
            if await is_banned_user(member.id):
                try: await message.chat.ban_member(member.id)
                except: pass
            if member.id == client.me.id:
                chat = message.chat
                adder = message.from_user
                if chat.id in await blacklisted_chats():
                    await message.reply_text(_["start_5"].format(f"@{config.BOT_USERNAME}", f"https://t.me/{config.BOT_USERNAME}?start=sudolist", config.SUPPORT_CHAT), disable_web_page_preview=True)
                    return await app.leave_chat(chat.id)
                try:
                    from SHUKLAMUSIC.core.userbot import assistantids
                    for ast_id in assistantids:
                        try:
                            ast_member = await app.get_chat_member(chat.id, ast_id)
                            if ast_member.status.value == "banned":
                                await message.reply_text(
                                    f"• <b>ᴀssɪsᴛᴀɴᴛ ɪs ʙᴀɴ ɪɴ ᴛʜɪs ᴄʜᴀᴛ!</b>\n\n"
                                    f"• <b>ᴘʟs ᴜɴʙᴀɴ ᴛʜᴇ ᴀssɪsᴛᴀɴᴛ ғɪʀsᴛ:</b>\n\n"
                                    f"• <b>ᴀssɪsᴛᴀɴᴛ ɪᴅ:</b> <code>{ast_id}</code>\n\n"
                                    f"• <b>ᴜɴʙᴀɴ ᴛʜᴇ ᴀssɪsᴛᴀɴᴛ ᴛʜᴇɴ ᴀɢᴀɪɴ ᴘʟᴀʏ</b>",
                                )
                        except Exception:
                            pass
                except Exception:
                    pass
                await message.reply_photo(
                    random.choice(SHASHANK_IMG),
                    caption=(
                        f"✨ <b>ʜᴇʏ {message.from_user.mention if message.from_user else 'ᴛʜᴇʀᴇ'}!</b>\n\n"
                        f"🎵 <b>ᴛʜᴀɴᴋs ғᴏʀ ᴀᴅᴅɪɴɢ ᴍᴇ ᴛᴏ</b> <b>{chat.title}</b>!\n\n"
                        f"• ɪ ᴀᴍ ᴀ ᴘᴏᴡᴇʀғᴜʟ ᴍᴜsɪᴄ ʙᴏᴛ\n"
                        f"• ʜɪɢʜ ǫᴜᴀʟɪᴛʏ ᴀᴜᴅɪᴏ & ᴠɪᴅᴇᴏ sᴛʀᴇᴀᴍɪɴɢ\n"
                        f"• ᴜsᴇ /play ᴛᴏ sᴛᴀʀᴛ ᴍᴜsɪᴄ 🎶\n\n"
                        f"❤️ <i>ʟᴇᴛ ᴛʜᴇ ᴍᴜsɪᴄ ʙᴇɢɪɴ!</i>"
                    ),
                    reply_markup=InlineKeyboardMarkup([
                        [
                            InlineKeyboardButton("• sᴜᴘᴘᴏʀᴛ ɢʀᴏᴜᴘ •", url=config.SUPPORT_CHAT),
                            InlineKeyboardButton("• ᴜᴘᴅᴀᴛᴇs •", url=config.SUPPORT_CHANNEL),
                        ]
                    ]),
                    parse_mode=enums.ParseMode.HTML,
                )
                await add_served_chat(chat.id)
        except Exception as ex:
            print(ex)

@app.on_callback_query(filters.regex("^close$") & ~BANNED_USERS)
async def close_message(client, cq):
    try: await cq.message.delete()
    except:
        try: await cq.answer("ᴄʟᴏsᴇᴅ", show_alert=False)
        except: pass

@app.on_callback_query(filters.regex("^shiv_Shashank$") & ~BANNED_USERS)
async def about_callback(client, cq):
    try: await cq.answer()
    except: pass
    back = InlineKeyboardMarkup([[InlineKeyboardButton("« ʙᴀᴄᴋ", callback_data="settings_back_helper")]])
    text = (
        f"<b>❖ ᴀʙᴏᴜᴛ ʙᴏᴛ</b>\n\n"
        f"๏ <b>ɴᴀᴍᴇ :</b> <a href='https://t.me/{config.BOT_USERNAME}'>{config.BOT_NAME}</a>\n"
        f"๏ <b>ᴜsᴇʀɴᴀᴍᴇ :</b> <a href='https://t.me/{config.BOT_USERNAME}'>@{config.BOT_USERNAME}</a>\n"
        f"๏ <b>sᴜᴘᴘᴏʀᴛ :</b> <a href='{config.SUPPORT_CHAT}'>ᴄʟɪᴄᴋ ʜᴇʀᴇ</a>\n\n"
        f"๏ <b>ʟᴀɴɢᴜᴀɢᴇ :</b> <a href='https://python.org'>ᴘʏᴛʜᴏɴ 3.11</a>\n"
        f"๏ <b>ᴅᴀᴛᴀʙᴀsᴇ :</b> <a href='https://supabase.com'>sᴜᴘᴀʙᴀsᴇ</a>\n"
        f"๏ <b>ʟɪʙʀᴀʀɪᴇs :</b> "
        f"<a href='https://docs.pyrogram.org'>ᴘʏʀᴏɢʀᴀᴍ</a> · "
        f"<a href='https://pytgcalls.github.io'>ᴘʏᴛɢᴄᴀʟʟs</a> · "
        f"<a href='https://github.com/yt-dlp/yt-dlp'>ʏᴛ-ᴅʟᴘ</a>\n"
        f"๏ <b>ʜᴏsᴛ :</b> <a href='https://render.com'>ʀᴇɴᴅᴇʀ</a>\n"
        f"๏ <b>sᴛʀᴇᴀᴍɪɴɢ :</b> ᴀᴜᴅɪᴏ & ᴠɪᴅᴇᴏ\n"
    )
    try:
        await cq.edit_message_caption(
            caption=text,
            reply_markup=back,
            parse_mode=enums.ParseMode.HTML,
        )
    except:
        try:
            await cq.edit_message_text(
                text,
                reply_markup=back,
                parse_mode=enums.ParseMode.HTML,
                disable_web_page_preview=True,
            )
        except: pass

# ══════════════════════════════════════════════════════════
#  SETTINGS BACK → restores start menu (photo + buttons)
# ══════════════════════════════════════════════════════════
@app.on_callback_query(filters.regex("^settings_back_helper$") & ~BANNED_USERS)
async def settings_back_helper(client, cq):
    try: await cq.answer()
    except: pass
    try:
        language = await get_lang(cq.from_user.id)
        _ = get_string(language)
        out = private_panel(_)
        served_chats = len(await get_served_chats())
        served_users = len(await get_served_users())
        UP, CPU, RAM, DISK = await bot_sys_stats()
        caption = _["start_2"].format(
            cq.from_user.mention, f"@{config.BOT_USERNAME}",
            UP, DISK, CPU, RAM, served_users, served_chats
        )
        from pyrogram.types import InputMediaPhoto
        await cq.message.edit_media(
            InputMediaPhoto(
                media=random.choice(SHASHANK_IMG),
                caption=caption,
            ),
            reply_markup=InlineKeyboardMarkup(out),
        )
    except Exception as e:
        print(f"back error: {e}")


# ══════════════════════════════════════════════════════════
#  HELP & COMMANDS — modules menu
# ══════════════════════════════════════════════════════════

MODULES = {
    "🎵 ᴘʟᴀʏ": {
        "cb": "help_play",
        "text": (
            "🎵 <b>ᴘʟᴀʏ ᴍᴏᴅᴜʟᴇ</b>\n\n"
            "<b>/play</b> — ᴀᴜᴅɪᴏ sᴛʀᴇᴀᴍ\n"
            "<b>/vplay</b> — ᴠɪᴅᴇᴏ sᴛʀᴇᴀᴍ\n"
            "<b>/cplay</b> — ᴄʜᴀɴɴᴇʟ ᴀᴜᴅɪᴏ\n"
            "<b>/cvplay</b> — ᴄʜᴀɴɴᴇʟ ᴠɪᴅᴇᴏ\n"
            "<b>/playforce</b> — sᴋɪᴘ & ᴘʟᴀʏ"
        ),
    },
    "⏭ sᴋɪᴘ": {
        "cb": "help_skip",
        "text": (
            "⏭ <b>sᴋɪᴘ ᴍᴏᴅᴜʟᴇ</b>\n\n"
            "<b>/skip</b> — sᴋɪᴘ ᴄᴜʀʀᴇɴᴛ sᴏɴɢ\n"
            "<b>/vskip</b> — sᴋɪᴘ ᴠɪᴅᴇᴏ sᴛʀᴇᴀᴍ\n\n"
            "<i>ᴀᴅᴍɪɴ / ᴀᴜᴛʜ ᴏɴʟʏ</i>"
        ),
    },
    "🛑 sᴛᴏᴘ": {
        "cb": "help_stop",
        "text": (
            "🛑 <b>sᴛᴏᴘ ᴍᴏᴅᴜʟᴇ</b>\n\n"
            "<b>/stop</b> — ᴇɴᴅ sᴛʀᴇᴀᴍ & ʟᴇᴀᴠᴇ ᴠᴄ\n"
            "<b>/end</b> — sᴀᴍᴇ ᴀs /sᴛᴏᴘ\n\n"
            "<i>ᴀᴅᴍɪɴ / ᴀᴜᴛʜ ᴏɴʟʏ</i>"
        ),
    },
    "⏸ ᴘᴀᴜsᴇ": {
        "cb": "help_pause",
        "text": (
            "⏸ <b>ᴘᴀᴜsᴇ / ʀᴇsᴜᴍᴇ</b>\n\n"
            "<b>II</b> — ᴘᴀᴜsᴇ  |  <b>▷</b> — ʀᴇsᴜᴍᴇ\n"
            "<b>« 10s / 10s »</b> — sᴇᴇᴋ ʙᴀᴄᴋ/ғᴏʀᴡᴀʀᴅ\n"
            "<b>⟨⟨</b> — ʀᴇᴘʟᴀʏ  |  <b>‣‣I</b> — ɴᴇxᴛ"
        ),
    },
    "🔐 ᴀᴜᴛʜ": {
        "cb": "help_auth",
        "text": (
            "🔐 <b>ᴀᴜᴛʜ ᴍᴏᴅᴜʟᴇ</b>\n\n"
            "<b>/auth</b> — ɢɪᴠᴇ ᴄᴏɴᴛʀᴏʟ ᴛᴏ ᴜsᴇʀ\n"
            "<b>/unauth</b> — ʀᴇᴍᴏᴠᴇ ᴀᴜᴛʜ\n"
            "<b>/authusers</b> — ᴠɪᴇᴡ ʟɪsᴛ\n\n"
            "<i>ɢʀᴏᴜᴘ ᴀᴅᴍɪɴ ᴏɴʟʏ</i>"
        ),
    },
    "📊 sᴛᴀᴛs": {
        "cb": "help_stats",
        "text": (
            "📊 <b>sᴛᴀᴛs ᴍᴏᴅᴜʟᴇ</b>\n\n"
            "<b>/stats</b> — ʙᴏᴛ ᴏᴠᴇʀᴀʟʟ sᴛᴀᴛs\n"
            "<b>/ping</b> — ᴄʜᴇᴄᴋ ʀᴇsᴘᴏɴsᴇ ᴛɪᴍᴇ"
        ),
    },
    "🌐 ᴘʟᴀᴛғᴏʀᴍs": {
        "cb": "help_platforms",
        "text": (
            "🌐 <b>sᴜᴘᴘᴏʀᴛᴇᴅ ᴘʟᴀᴛғᴏʀᴍs</b>\n\n"
            "✅ ʏᴏᴜᴛᴜʙᴇ\n"
            "✅ sᴘᴏᴛɪғʏ\n"
            "✅ ᴀᴘᴘʟᴇ ᴍᴜsɪᴄ\n"
            "✅ sᴏᴜɴᴅᴄʟᴏᴜᴅ\n"
            "✅ ʀᴇssᴏ\n"
            "✅ ᴛᴇʟᴇɢʀᴀᴍ ᴀᴜᴅɪᴏ"
        ),
    },
    "🚫 ᴀʙᴜsᴇ": {
        "cb": "help_abuse",
        "text": (
            "🚫 <b>ɴᴏ-ᴀʙᴜsᴇ ᴍᴏᴅᴜʟᴇ</b>\n\n"
            "<b>/noabuse on</b>  — ᴇɴᴀʙʟᴇ ✅\n"
            "<b>/noabuse off</b> — ᴅɪsᴀʙʟᴇ ❌\n\n"
            "🛡 <b>ʜᴏᴡ ɪᴛ ᴡᴏʀᴋs:</b>\n"
            "• ɢᴀʟɪ ᴅᴇᴛᴇᴄᴛ ʜᴏᴛɪ ʜᴀɪ → ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ\n"
            "• ʜɪɴᴅɪ / ᴘᴜɴᴊᴀʙɪ / ᴇɴɢʟɪsʜ sᴀʙ ᴅᴇᴛᴇᴄᴛ\n"
            "• ᴀᴅᴍɪɴ ʜᴏ ʏᴀ ɴᴀ ʜᴏ — sᴀʙ ᴇǫᴜᴀʟ\n"
            "• ᴡᴀʀɴɪɴɢ 10 sᴇᴄ ʙᴀᴀᴅ ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ\n\n"
            "<i>ɢʀᴏᴜᴘ ᴀᴅᴍɪɴ ᴏɴʟʏ</i>"
        ),
    },
    "🔇 ʙʟ ᴄʜᴀᴛ": {
        "cb": "help_blchat",
        "text": (
            "🔇 <b>ʙʟ ᴄʜᴀᴛ ᴍᴏᴅᴜʟᴇ</b>\n\n"
            "<b>/blacklist &lt;word&gt;</b> — ᴀᴅᴅ ᴀ ᴡᴏʀᴅ ᴛᴏ ʙʟᴀᴄᴋʟɪsᴛ 🚫\n"
            "<b>/unblacklist &lt;word&gt;</b> — ʀᴇᴍᴏᴠᴇ ᴀ ᴡᴏʀᴅ 🗑\n"
            "<b>/blacklistview</b> — ᴠɪᴇᴡ ᴀʟʟ ʙʟᴀᴄᴋʟɪsᴛᴇᴅ ᴡᴏʀᴅs 📋\n\n"
            "🛡 <b>ʜᴏᴡ ɪᴛ ᴡᴏʀᴋs:</b>\n"
            "• ᴡᴏʀᴅ ᴀᴅᴅᴇᴅ ᴠɪᴀ /blacklist → ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇᴅ\n"
            "• ᴇᴀᴄʜ ɢʀᴏᴜᴘ ʜᴀs ɪᴛs ᴏᴡɴ sᴇᴘᴀʀᴀᴛᴇ ʟɪsᴛ\n"
            "• ᴡᴏʀᴅs sᴛᴀʏ sᴀᴠᴇᴅ ᴇᴠᴇɴ ᴀꜰᴛᴇʀ ʙᴏᴛ ʀᴇsᴛᴀʀᴛ\n\n"
            "<i>ɢʀᴏᴜᴘ ᴀᴅᴍɪɴ ᴏɴʟʏ</i>"
        ),
    },
    "🛡 ᴍᴏᴅᴇʀᴀᴛɪᴏɴ": {
        "cb": "help_moderation",
        "text": (
            "🛡 <b>ᴍᴏᴅᴇʀᴀᴛɪᴏɴ ᴍᴏᴅᴜʟᴇ</b>\n\n"
            "<b>/mute</b> — ᴍᴜᴛᴇ ᴀ ᴜsᴇʀ\n"
            "<b>/unmute</b> — ᴜɴᴍᴜᴛᴇ ᴀ ᴜsᴇʀ\n"
            "<b>/ban</b> — ʙᴀɴ ᴀ ᴜsᴇʀ\n"
            "<b>/unban</b> — ᴜɴʙᴀɴ ᴀ ᴜsᴇʀ\n"
            "<b>/kick</b> — ᴋɪᴄᴋ ᴀ ᴜsᴇʀ\n\n"
            "<i>ʀᴇᴘʟʏ ᴛᴏ ᴜsᴇʀ ᴏʀ ᴘʀᴏᴠɪᴅᴇ @ᴜsᴇʀɴᴀᴍᴇ</i>\n"
            "<i>ɢʀᴏᴜᴘ ᴀᴅᴍɪɴ ᴏɴʟʏ</i>"
        ),
    },
}

def _help_main_markup():
    rows = []
    items = list(MODULES.items())
    for i in range(0, len(items), 2):
        row = [InlineKeyboardButton(items[i][0], callback_data=items[i][1]["cb"])]
        if i + 1 < len(items):
            row.append(InlineKeyboardButton(items[i+1][0], callback_data=items[i+1][1]["cb"]))
        rows.append(row)
    rows.append([InlineKeyboardButton("« ʙᴀᴄᴋ", callback_data="settings_back_helper")])
    return InlineKeyboardMarkup(rows)

def _module_markup(cb_key):
    return InlineKeyboardMarkup([[InlineKeyboardButton("« ʙᴀᴄᴋ ᴛᴏ ʜᴇʟᴩ", callback_data="help_main")]])


@app.on_callback_query(filters.regex("^help_main$") & ~BANNED_USERS)
async def help_main_cb(client, cq):
    try: await cq.answer()
    except: pass
    caption = (
        "<b>❖ ʜᴇʟᴩ & ᴄᴏᴍᴍᴀɴᴅs</b>\n\n"
        "ᴄʟɪᴄᴋ ᴏɴ ᴀɴʏ ᴍᴏᴅᴜʟᴇ ʙᴜᴛᴛᴏɴ\n"
    )
    try:
        await cq.edit_message_caption(caption=caption, reply_markup=_help_main_markup())
    except:
        try:
            await cq.edit_message_text(caption, reply_markup=_help_main_markup())
        except: pass




# Individual module callbacks
for _mod_name, _mod_data in MODULES.items():
    def _make_handler(data):
        async def _handler(client, cq):
            try: await cq.answer()
            except: pass
            try:
                await cq.edit_message_caption(
                    caption=data["text"],
                    reply_markup=_module_markup(data["cb"]),
                )
            except:
                try:
                    await cq.edit_message_text(
                        data["text"],
                        reply_markup=_module_markup(data["cb"]),
                    )
                except: pass
        return _handler
    app.on_callback_query(
        filters.regex(f"^{_mod_data['cb']}$") & ~BANNED_USERS
    )(_make_handler(_mod_data))


@app.on_callback_query(filters.regex("^help_start$") & ~BANNED_USERS)
async def help_start_trigger(client, cq):
    try: await cq.answer()
    except: pass
    caption = (
        "<b>❖ ʜᴇʟᴩ & ᴄᴏᴍᴍᴀɴᴅs</b>\n\n"
        "ᴄʟɪᴄᴋ ᴏɴ ᴀɴʏ ᴍᴏᴅᴜʟᴇ ʙᴜᴛᴛᴏɴ\n"
    )
    try:
        await cq.edit_message_caption(caption=caption, reply_markup=_help_main_markup())
    except:
        try:
            await cq.edit_message_text(caption, reply_markup=_help_main_markup())
        except: pass


@app.on_callback_query(filters.regex("^source_alert$") & ~BANNED_USERS)
async def source_alert(client, cq):
    await cq.answer("ʀᴇᴘᴏ ᴋʏᴀ ʟᴇɢᴀ ᴘᴀɴᴅᴀ ᴋᴀ ʟᴜɴᴅ ʟᴇʟᴇ ʙᴏʟ ʟᴇɢᴀ 🤣🤣", show_alert=True)
