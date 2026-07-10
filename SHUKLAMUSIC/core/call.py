import asyncio
import os
import shutil
import sys
from datetime import datetime, timedelta

# Setup static-ffmpeg so pytgcalls can find ffmpeg even on restricted hosts
try:
    import static_ffmpeg
    static_ffmpeg.add_paths()  # adds bundled ffmpeg/ffprobe to PATH
except Exception:
    pass

# Patch pytgcalls ffmpeg check to bypass PATH issues on restricted hosts (fallback)
import pytgcalls.ffmpeg as _pytgcalls_ffmpeg
import pytgcalls.types.stream.media_stream as _ms

async def _noop_check(*args, **kwargs):
    pass

_pytgcalls_ffmpeg.check_stream = _noop_check
_ms.check_stream = _noop_check
from typing import Union
from ntgcalls import ConnectionNotFound, TelegramServerError
from pyrogram import Client
from pyrogram.errors import ChannelInvalid, ChannelPrivate, PeerIdInvalid
from pyrogram.types import InlineKeyboardMarkup, ChatPrivileges
from pytgcalls import PyTgCalls, exceptions, types
from pytgcalls.pytgcalls_session import PyTgCallsSession
import config
from SHUKLAMUSIC import LOGGER, YouTube, app
from SHUKLAMUSIC.misc import db
from SHUKLAMUSIC.helpers import (add_active_chat, add_active_video_chat, get_lang, get_loop, group_assistant, is_autoend, music_on, remove_active_chat, remove_active_video_chat, set_loop)
from SHUKLAMUSIC.helpers import AssistantErr
from SHUKLAMUSIC.helpers import seconds_to_min
from SHUKLAMUSIC.helpers import stream_markup
from SHUKLAMUSIC.helpers import auto_clean
from SHUKLAMUSIC.helpers import get_thumb as gen_thumb
from SHUKLAMUSIC.helpers import get_string

autoend = {}
counter = {}

async def _clear_(chat_id: int):
    db[chat_id] = []
    await remove_active_video_chat(chat_id)
    await remove_active_chat(chat_id)

class Call(PyTgCalls):
    def __init__(self):
        PyTgCallsSession.notice_displayed = True

        self.userbot1 = Client(
            name="SHUKLAAss1",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING1),
        )
        self.one = PyTgCalls(self.userbot1, cache_duration=100)

        self.userbot2 = Client(
            name="SHUKLAAss2",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING2),
        )
        self.two = PyTgCalls(self.userbot2, cache_duration=100)

        self.userbot3 = Client(
            name="SHUKLAAss3",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING3),
        )
        self.three = PyTgCalls(self.userbot3, cache_duration=100)

        self.userbot4 = Client(
            name="SHUKLAAss4",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING4),
        )
        self.four = PyTgCalls(self.userbot4, cache_duration=100)

        self.userbot5 = Client(
            name="SHUKLAAss5",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING5),
        )
        self.five = PyTgCalls(self.userbot5, cache_duration=100)

    def _build_stream(
        self,
        source: str,
        video: bool,
        ffmpeg: str | None = None,
    ) -> types.MediaStream:
        video_flags = (
            types.MediaStream.Flags.AUTO_DETECT
            if video
            else types.MediaStream.Flags.IGNORE
        )
        return types.MediaStream(
            media_path=source,
            audio_parameters=types.AudioQuality.MEDIUM,
            video_parameters=types.VideoQuality.SD_480p,
            audio_flags=types.MediaStream.Flags.REQUIRED,
            video_flags=video_flags,
            ffmpeg_parameters=ffmpeg,
        )

    async def _play_on_assistant(
        self,
        client: PyTgCalls,
        chat_id: int,
        stream: types.MediaStream,
    ):
        try:
            await client.play(chat_id, stream)
        except (ChannelInvalid, ChannelPrivate, PeerIdInvalid):
            raise
        except Exception as e:
            err = str(e).lower()
            err_type = type(e).__name__.lower()
            if "already" in err or "joined" in err:
                try:
                    await client.play(chat_id, stream)
                except Exception:
                    pass
            elif "noactivegroupcall" in err or "no active" in err:
                raise exceptions.NoActiveGroupCall
            elif "channelinvalid" in err or "channel_invalid" in err or "peerid" in err_type:
                raise ChannelInvalid(0)
            elif "shellerror" in err_type or "no such file" in err or "default_launcher" in err:
                raise FileNotFoundError("ntgcalls shell error")
            else:
                raise

    async def pause_stream(self, chat_id: int):
        assistant = await group_assistant(self, chat_id)
        await assistant.pause(chat_id)

    async def resume_stream(self, chat_id: int):
        assistant = await group_assistant(self, chat_id)
        await assistant.resume(chat_id)

    async def stop_stream(self, chat_id: int):
        assistant = await group_assistant(self, chat_id)
        try:
            await _clear_(chat_id)
            await assistant.leave_call(chat_id, close=False)
        except Exception:
            pass

    async def stop_stream_force(self, chat_id: int):
        for string, client in [
            (config.STRING1, self.one),
            (config.STRING2, self.two),
            (config.STRING3, self.three),
            (config.STRING4, self.four),
            (config.STRING5, self.five),
        ]:
            if not string:
                continue
            try:
                await client.leave_call(chat_id, close=False)
            except Exception:
                pass
        try:
            await _clear_(chat_id)
        except Exception:
            pass

    async def speedup_stream(self, chat_id: int, file_path, speed, playing):
        assistant = await group_assistant(self, chat_id)
        if str(speed) != "1.0":
            base = os.path.basename(file_path)
            chatdir = os.path.join(os.getcwd(), "playback", str(speed))
            if not os.path.isdir(chatdir):
                os.makedirs(chatdir)
            out = os.path.join(chatdir, base)
            if not os.path.isfile(out):
                if str(speed) == "0.5":
                    vs = 2.0
                elif str(speed) == "0.75":
                    vs = 1.35
                elif str(speed) == "1.5":
                    vs = 0.68
                elif str(speed) == "2.0":
                    vs = 0.5
                else:
                    vs = 1.0
                proc = await asyncio.create_subprocess_shell(
                    cmd=(
                        "ffmpeg "
                        "-i "
                        f"{file_path} "
                        "-filter:v "
                        f"setpts={vs}*PTS "
                        "-filter:a "
                        f"atempo={speed} "
                        f"{out}"
                    ),
                    stdin=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
                await proc.communicate()
        else:
            out = file_path
        dur = await asyncio.get_event_loop().run_in_executor(None, check_duration, out)
        dur = int(dur)
        played, con_seconds = speed_converter(playing[0]["played"], speed)
        duration = seconds_to_min(dur)
        xx = f"-ss {played} -to {duration}"
        video_mode = playing[0]["streamtype"] == "video"
        stream = self._build_stream(out, video=video_mode, ffmpeg=xx)
        if str(db[chat_id][0]["file"]) == str(file_path):
            await self._play_on_assistant(assistant, chat_id, stream)
        else:
            raise AssistantErr("Umm")
        if str(db[chat_id][0]["file"]) == str(file_path):
            exis = (playing[0]).get("old_dur")
            if not exis:
                db[chat_id][0]["old_dur"] = db[chat_id][0]["dur"]
                db[chat_id][0]["old_second"] = db[chat_id][0]["seconds"]
            db[chat_id][0]["played"] = con_seconds
            db[chat_id][0]["dur"] = duration
            db[chat_id][0]["seconds"] = dur
            db[chat_id][0]["speed_path"] = out
            db[chat_id][0]["speed"] = speed

    async def force_stop_stream(self, chat_id: int):
        assistant = await group_assistant(self, chat_id)
        try:
            check = db.get(chat_id)
            check.pop(0)
        except Exception:
            pass
        await remove_active_video_chat(chat_id)
        await remove_active_chat(chat_id)
        try:
            await assistant.leave_call(chat_id, close=False)
        except Exception:
            pass

    async def skip_stream(
        self,
        chat_id: int,
        link: str,
        video: Union[bool, str] = None,
        image: Union[bool, str] = None,
    ):
        assistant = await group_assistant(self, chat_id)
        stream = self._build_stream(link, video=bool(video))
        await self._play_on_assistant(assistant, chat_id, stream)

    async def seek_stream(self, chat_id, file_path, to_seek, duration, mode):
        assistant = await group_assistant(self, chat_id)
        ffmpeg = f"-ss {to_seek} -to {duration}"
        video_mode = mode == "video"
        stream = self._build_stream(
            file_path,
            video=video_mode,
            ffmpeg=ffmpeg,
        )
        await self._play_on_assistant(assistant, chat_id, stream)

    async def stream_call(self, link):
        # Only validate that the stream URL is reachable — do NOT join/leave any VC.
        # Previously this joined LOGGER_ID VC and immediately left (0.2s), which caused
        # the assistant to join the group VC and leave within 1 second on every /play.
        import aiohttp
        try:
            async with aiohttp.ClientSession() as session:
                async with session.head(link, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                    if resp.status >= 400:
                        raise Exception(f"Stream URL returned HTTP {resp.status}")
        except Exception:
            # If we can't validate (e.g. non-HTTP stream), just pass through.
            # The actual join_call will raise NoActiveGroupCall if VC is not started.
            pass

    def _get_pyrogram_client(self, assistant):
        """PyTgCalls assistant se uska Pyrogram/Kurigram client nikalo."""
        pairs = [
            (self.userbot1, self.one),
            (self.userbot2, self.two),
            (self.userbot3, self.three),
            (self.userbot4, self.four),
            (self.userbot5, self.five),
        ]
        for userbot, pytgcalls_client in pairs:
            if pytgcalls_client is assistant:
                return userbot
        return None

    async def _invite_and_retry(self, assistant, chat_id, original_chat_id, link, video, image, _):
        """Invite assistant to group via invite link (if bot is admin), else add directly. Then retry stream."""
        from SHUKLAMUSIC import app as _app
        import asyncio

        # Inviting message bhejo
        try:
            invite_msg = await _app.send_message(
                original_chat_id,
                "⏳ <b>ɪɴᴠɪᴛɪɴɢ ᴀssɪsᴛᴀɴᴛ ɪɴᴛᴏ ɢʀᴏᴜᴘ...</b>",
            )
        except Exception:
            invite_msg = None

        # Is assistant ka Pyrogram/Kurigram client nikalo
        pyrogram_client = self._get_pyrogram_client(assistant)

        joined = False

        # Assistant ki info pehle nikalo (ban check ke liye zaroori)
        asst_me = pyrogram_client.me if pyrogram_client else None
        if asst_me is None and pyrogram_client:
            try:
                asst_me = await pyrogram_client.get_me()
            except Exception:
                pass
        asst_id = asst_me.id if asst_me else "Unknown"
        asst_username = f"@{asst_me.username}" if (asst_me and asst_me.username) else f"ID: <code>{asst_id}</code>"

        def _is_banned_err(e: Exception) -> bool:
            """Check karo ki error ban ki wajah se hai ya nahi."""
            err = str(e).lower()
            err_type = type(e).__name__.lower()
            ban_keywords = ["banned", "kicked", "userbanned", "userkicked",
                            "user_banned", "user_kicked", "chat_write_forbidden",
                            "you were banned", "forbidden"]
            return any(k in err or k in err_type for k in ban_keywords)

        # Method 1: Bot admin hai — invite link banao, assistant khud join kare
        if pyrogram_client:
            try:
                link_obj = await _app.create_chat_invite_link(chat_id)
                inv_link = getattr(link_obj, "invite_link", None) or getattr(link_obj, "link", None)
                if inv_link:
                    await pyrogram_client.join_chat(inv_link)
                    await asyncio.sleep(2)
                    joined = True
            except Exception as join_err:
                if _is_banned_err(join_err):
                    if invite_msg:
                        try: await invite_msg.delete()
                        except: pass
                    raise AssistantErr(
                        f"❖ <b>Assistant Is Banned In This Group</b>\n\n"
                        f"Assistant account is banned from this group.\n"
                        f"Please unban the assistant and try again.\n\n"
                        f"<b>Assistant:</b> {asst_username}\n"
                        f"<b>User ID:</b> <code>{asst_id}</code>"
                    )
                pass  # Ban nahi, koi aur issue — fallback try karo

        # Method 2: Fallback — bot directly add kare (add_members permission chahiye)
        if not joined:
            try:
                await _app.add_chat_members(chat_id, asst_id)
                await asyncio.sleep(3)
            except Exception as add_err:
                if invite_msg:
                    try: await invite_msg.delete()
                    except: pass
                if _is_banned_err(add_err):
                    raise AssistantErr(
                        f"❖ <b>Assistant Is Banned In This Group</b>\n\n"
                        f"Assistant account is banned from this group.\n"
                        f"Please unban the assistant and try again.\n\n"
                        f"<b>Assistant:</b> {asst_username}\n"
                        f"<b>User ID:</b> <code>{asst_id}</code>"
                    )
                raise AssistantErr(
                    f"❖ <b>Assistant Not In Group</b>\n\n"
                    f"Please add the assistant manually and try again.\n"
                    f"<b>Assistant:</b> {asst_username}\n"
                    f"<b>User ID:</b> <code>{asst_id}</code>\n"
                    f"Error: <code>{type(add_err).__name__}</code>"
                )

        # Assistant ko admin banana try karo (silently fail karo agar bot ke paas rights nahi)
        try:
            me = pyrogram_client.me if pyrogram_client else None
            if me is None and pyrogram_client:
                me = await pyrogram_client.get_me()
            if me:
                await _app.promote_chat_member(
                    chat_id,
                    me.id,
                    privileges=ChatPrivileges(
                        can_manage_chat=True,
                        can_delete_messages=True,
                        can_manage_video_chats=True,
                        can_restrict_members=False,
                        can_promote_members=False,
                        can_change_info=False,
                        can_invite_users=True,
                        can_pin_messages=False,
                        is_anonymous=False,
                    ),
                )
        except Exception:
            pass  # Bot ke paas promote rights nahi — koi baat nahi, music play hoga

        # Stream retry karo
        try:
            stream = self._build_stream(link, video=bool(video))
            await self._play_on_assistant(assistant, chat_id, stream)
            if invite_msg:
                try: await invite_msg.delete()
                except: pass
            await add_active_chat(chat_id)
            await music_on(chat_id)
            if video:
                await add_active_video_chat(chat_id)
        except Exception as retry_err:
            if invite_msg:
                try: await invite_msg.delete()
                except: pass
            raise AssistantErr(
                f"❖ <b>Stream failed after invite</b>\n"
                f"Error: <code>{type(retry_err).__name__}</code>"
            )

    async def join_call(
        self,
        chat_id: int,
        original_chat_id: int,
        link,
        video: Union[bool, str] = None,
        image: Union[bool, str] = None,
    ):
        assistant = await group_assistant(self, chat_id)
        language = await get_lang(chat_id)
        _ = get_string(language)
        stream = self._build_stream(link, video=bool(video))
        try:
            await self._play_on_assistant(assistant, chat_id, stream)
        except exceptions.NoActiveGroupCall:
            raise AssistantErr(_["call_8"])
        except exceptions.NoAudioSourceFound:
            raise AssistantErr(_["call_10"])
        except ConnectionNotFound:
            raise AssistantErr(_["call_10"])
        except TelegramServerError:
            # TelegramServerError tab bhi aata hai jab assistant group ka member nahi hota
            # (unban hua ho lekin re-add nahi hua). Pehle invite flow try karo.
            try:
                await self._invite_and_retry(assistant, chat_id, original_chat_id, link, video, image, _)
                return
            except AssistantErr:
                raise
            except Exception:
                raise AssistantErr(_["call_10"])
        except (ChannelInvalid, ChannelPrivate, PeerIdInvalid):
            await self._invite_and_retry(assistant, chat_id, original_chat_id, link, video, image, _)
            return
        except (FileNotFoundError, Exception) as e:
            err_str = str(e).lower()
            err_type = type(e).__name__.lower()
            # ChannelInvalid can also appear wrapped inside generic Exception
            if "channelinvalid" in err_str or "channel_invalid" in err_str or "peerid" in err_str:
                await self._invite_and_retry(assistant, chat_id, original_chat_id, link, video, image, _)
                return
            # ShellError / ffmpeg path issue — retry with audio-only stream
            elif "shellero" in err_type or "filenotfound" in err_type or "no such file" in err_str:
                try:
                    audio_stream = types.MediaStream(
                        media_path=link,
                        audio_parameters=types.AudioQuality.HIGH,
                        audio_flags=types.MediaStream.Flags.REQUIRED,
                        video_flags=types.MediaStream.Flags.IGNORE,
                    )
                    await self._play_on_assistant(assistant, chat_id, audio_stream)
                except (ChannelInvalid, ChannelPrivate, PeerIdInvalid):
                    raise AssistantErr(
                        "❖ <b>Assistant Not In Group</b>\n\n"
                        "Please <b>add the assistant account</b> to your group first, then try again."
                    )
                except Exception:
                    raise AssistantErr(_["call_10"])
            else:
                raise AssistantErr(_["call_10"])
        await add_active_chat(chat_id)
        await music_on(chat_id)
        if video:
            await add_active_video_chat(chat_id)
        if await is_autoend():
            counter[chat_id] = {}
            users = len(await assistant.get_participants(chat_id))
            if users == 1:
                autoend[chat_id] = datetime.now() + timedelta(minutes=1)

    async def change_stream(self, client: PyTgCalls, chat_id: int):
        check = db.get(chat_id)
        popped = None
        loop = await get_loop(chat_id)
        try:
            if loop == 0:
                popped = check.pop(0)
            else:
                loop = loop - 1
                await set_loop(chat_id, loop)
            await auto_clean(popped)
            if not check:
                # Delete player panel
                try:
                    if popped and popped.get("mystic"):
                        await popped["mystic"].delete()
                except Exception:
                    pass
                # Send leave message
                try:
                    orig = popped.get("chat_id", chat_id) if popped else chat_id
                    language = await get_lang(chat_id)
                    _ = get_string(language)
                    await app.send_message(
                        orig,
                        "🎵 **ᴀssɪsᴛᴀɴᴛ ʟᴇᴀᴠᴇ ᴠᴄ sᴏɴɢ ᴋᴀʜᴀᴛᴍ** 🎵",
                    )
                except Exception:
                    pass
                await _clear_(chat_id)
                return await client.leave_call(chat_id, close=False)
        except Exception:
            try:
                await _clear_(chat_id)
                return await client.leave_call(chat_id, close=False)
            except Exception:
                return
        queued = check[0]["file"]
        language = await get_lang(chat_id)
        _ = get_string(language)
        title = (check[0]["title"]).title()
        user = check[0]["by"]
        original_chat_id = check[0]["chat_id"]
        streamtype = check[0]["streamtype"]
        videoid = check[0]["vidid"]
        db[chat_id][0]["played"] = 0
        import time as _time
        from SHUKLAMUSIC.plugins.admins import _start_time, start_progress_task
        _start_time[chat_id] = _time.time()
        start_progress_task(chat_id)
        exis = (check[0]).get("old_dur")
        if exis:
            db[chat_id][0]["dur"] = exis
            db[chat_id][0]["seconds"] = check[0]["old_second"]
            db[chat_id][0]["speed_path"] = None
            db[chat_id][0]["speed"] = 1.0
        video = True if str(streamtype) == "video" else False
        if "live_" in queued:
            n, link = await YouTube.video(videoid, True)
            if n == 0:
                return await app.send_message(
                    original_chat_id,
                    text=_["call_6"],
                )
            stream = self._build_stream(link, video=video)
            try:
                await self._play_on_assistant(client, chat_id, stream)
            except Exception:
                return await app.send_message(
                    original_chat_id,
                    text=_["call_6"],
                )
            img = await gen_thumb(videoid)
            button = stream_markup(_, chat_id)
            run = await app.send_photo(
                chat_id=original_chat_id,
                photo=img,
                caption=_["stream_1"].format(
                    f"https://t.me/{config.BOT_USERNAME}?start=info_{videoid}",
                    title[:23],
                    check[0]["dur"],
                    user,
                ),
                reply_markup=InlineKeyboardMarkup(button),
            )
            db[chat_id][0]["mystic"] = run
            db[chat_id][0]["markup"] = "tg"
        elif "vid_" in queued:
            mystic = await app.send_message(original_chat_id, _["call_7"])
            try:
                file_path, direct = await YouTube.download(
                    videoid,
                    mystic,
                    videoid=True,
                    video=video,
                )
            except Exception:
                return await mystic.edit_text(
                    _["call_6"], disable_web_page_preview=True
                )
            stream = self._build_stream(file_path, video=video)
            try:
                await self._play_on_assistant(client, chat_id, stream)
            except Exception:
                return await app.send_message(
                    original_chat_id,
                    text=_["call_6"],
                )
            img = await gen_thumb(videoid)
            button = stream_markup(_, chat_id)
            await mystic.delete()
            run = await app.send_photo(
                chat_id=original_chat_id,
                photo=img,
                caption=_["stream_1"].format(
                    f"https://t.me/{config.BOT_USERNAME}?start=info_{videoid}",
                    title[:23],
                    check[0]["dur"],
                    user,
                ),
                reply_markup=InlineKeyboardMarkup(button),
            )
            db[chat_id][0]["mystic"] = run
            db[chat_id][0]["markup"] = "stream"

        elif "index_" in queued:
            stream = self._build_stream(videoid, video=video)
            try:
                await self._play_on_assistant(client, chat_id, stream)
            except Exception:
                return await app.send_message(
                    original_chat_id,
                    text=_["call_6"],
                )
            button = stream_markup(_, chat_id)
            run = await app.send_photo(
                chat_id=original_chat_id,
                photo=config.STREAM_IMG_URL,
                caption=_["stream_2"].format(user),
                reply_markup=InlineKeyboardMarkup(button),
            )
            db[chat_id][0]["mystic"] = run
            db[chat_id][0]["markup"] = "tg"
        else:
            stream = self._build_stream(queued, video=video)
            try:
                await self._play_on_assistant(client, chat_id, stream)
            except Exception:
                return await app.send_message(
                    original_chat_id,
                    text=_["call_6"],
                )
            if videoid == "telegram":
                button = stream_markup(_, chat_id)
                run = await app.send_photo(
                    chat_id=original_chat_id,
                    photo=(
                        config.TELEGRAM_AUDIO_URL
                        if str(streamtype) == "audio"
                        else config.TELEGRAM_VIDEO_URL
                    ),
                    caption=_["stream_1"].format(
                        config.SUPPORT_GROUP, title[:23], check[0]["dur"], user
                    ),
                    reply_markup=InlineKeyboardMarkup(button),
                )
                db[chat_id][0]["mystic"] = run
                db[chat_id][0]["markup"] = "tg"
            elif videoid == "soundcloud":
                button = stream_markup(_, chat_id)
                run = await app.send_photo(
                    chat_id=original_chat_id,
                    photo=config.SOUNCLOUD_IMG_URL,
                    caption=_["stream_1"].format(
                        config.SUPPORT_GROUP, title[:23], check[0]["dur"], user
                    ),
                    reply_markup=InlineKeyboardMarkup(button),
                )
                db[chat_id][0]["mystic"] = run
                db[chat_id][0]["markup"] = "tg"
            else:
                img = await gen_thumb(videoid)
                button = stream_markup(_, chat_id)
                run = await app.send_photo(
                    chat_id=original_chat_id,
                    photo=img,
                    caption=_["stream_1"].format(
                        f"https://t.me/{config.BOT_USERNAME}?start=info_{videoid}",
                        title[:23],
                        check[0]["dur"],
                        user,
                    ),
                    reply_markup=InlineKeyboardMarkup(button),
                )
                db[chat_id][0]["mystic"] = run
                db[chat_id][0]["markup"] = "stream"

    async def ping(self):
        pings = []
        if config.STRING1:
            pings.append(self.one.ping)
        if config.STRING2:
            pings.append(self.two.ping)
        if config.STRING3:
            pings.append(self.three.ping)
        if config.STRING4:
            pings.append(self.four.ping)
        if config.STRING5:
            pings.append(self.five.ping)
        return str(round(sum(pings) / len(pings), 3)) if pings else "0"

    async def start(self):
        LOGGER(__name__).info("Starting PyTgCalls Client...\n")
        if config.STRING1:
            await self.one.start()
        if config.STRING2:
            await self.two.start()
        if config.STRING3:
            await self.three.start()
        if config.STRING4:
            await self.four.start()
        if config.STRING5:
            await self.five.start()

    async def decorators(self):
        for string, client in [
            (config.STRING1, self.one),
            (config.STRING2, self.two),
            (config.STRING3, self.three),
            (config.STRING4, self.four),
            (config.STRING5, self.five),
        ]:
            if not string:
                continue
            @client.on_update()
            async def _update_handler(_, update: types.Update, _client=client):
                if isinstance(update, types.StreamEnded):
                    if update.stream_type in [
                        types.StreamEnded.Type.AUDIO,
                        types.StreamEnded.Type.VIDEO,
                    ]:
                        await self.change_stream(_client, update.chat_id)
                elif isinstance(update, types.ChatUpdate):
                    if update.status in [
                        types.ChatUpdate.Status.KICKED,
                        types.ChatUpdate.Status.LEFT_GROUP,
                        types.ChatUpdate.Status.CLOSED_VOICE_CHAT,
                    ]:
                        await self.stop_stream(update.chat_id)

SHUKLA = Call()
