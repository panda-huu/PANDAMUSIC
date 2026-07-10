# ---------------------------------------------------------------
# 🔸 RADHExMUSIC — couple.py
# 🔹 /couple — 2 random members ka DP couple template me daalega
# ---------------------------------------------------------------

import html
import io
import os
import random

from PIL import Image, ImageDraw
from pyrogram import filters
from pyrogram.errors import ChatAdminRequired
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from SHUKLAMUSIC import app
from config import OWNER_USERNAME

COUPLE_TEXTS = [
    "💘 ᴀᴀᴊ ᴋᴀ ᴄᴏᴜᴘʟᴇ ᴏꜰ ᴛʜᴇ ᴅᴀʏ",
    "💑 ɢʀᴏᴜᴘ ɴᴇ ᴄʜᴜɴ ʟɪʏᴀ ᴀᴀᴊ ᴋᴀ ᴊᴏᴅᴀ",
    "🌹 ᴅɪʟ ᴍɪʟᴀ ᴅɪʏᴀ ʙʀᴀʜᴍᴀɴᴅ ɴᴇ",
    "💝 ᴋɪꜱᴍᴀᴛ ɴᴇ ᴍɪʟᴀʏᴀ ᴛᴜᴍʜᴇ",
    "🔥 ʏᴇ ᴅᴏɴᴏ ʙᴀɴᴇ ʜᴀɪɴ ᴇᴋ ᴅᴜᴊᴇ ᴋᴇ ʟɪʏᴇ",
]

TEMPLATE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "static", "COUPLE.png"
)

LEFT_CENTER  = (759, 924)
LEFT_RADIUS  = 500
RIGHT_CENTER = (2475, 898)
RIGHT_RADIUS = 497


def make_circle_avatar(img_bytes: bytes, radius: int) -> Image.Image:
    size = radius * 2
    try:
        avatar = Image.open(io.BytesIO(img_bytes)).convert("RGBA")
    except Exception:
        return make_default_avatar(radius)
    w, h = avatar.size
    min_side = min(w, h)
    left = (w - min_side) // 2
    top  = (h - min_side) // 2
    avatar = avatar.crop((left, top, left + min_side, top + min_side))
    avatar = avatar.resize((size, size), Image.LANCZOS)
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, size - 1, size - 1), fill=255)
    avatar.putalpha(mask)
    return avatar


def make_default_avatar(radius: int) -> Image.Image:
    size = radius * 2
    img  = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, size - 1, size - 1), fill=255)
    fill = Image.new("RGBA", (size, size), (100, 100, 100, 255))
    fill.putalpha(mask)
    img.paste(fill, (0, 0))
    draw = ImageDraw.Draw(img)
    cx, cy = size // 2, size // 2
    head_r = size // 7
    draw.ellipse(
        [cx - head_r, cy - size // 3 - head_r,
         cx + head_r, cy - size // 3 + head_r],
        fill=(160, 160, 160, 255),
    )
    draw.ellipse(
        [cx - size // 4, cy - size // 10,
         cx + size // 4, cy + size // 3],
        fill=(160, 160, 160, 255),
    )
    return img


async def get_user_avatar(client, user_id: int, radius: int) -> Image.Image:
    tmp_path = f"/tmp/couple_dp_{user_id}.jpg"
    try:
        # get_users kaam karta hai kurigram me — user.photo.big_file_id se download
        user = await client.get_users(user_id)
        if not user or not user.photo:
            return make_default_avatar(radius)
        saved = await client.download_media(
            user.photo.big_file_id, file_name=tmp_path
        )
        read_path = saved if (saved and os.path.exists(saved)) else tmp_path
        if read_path and os.path.exists(read_path) and os.path.getsize(read_path) > 0:
            with open(read_path, "rb") as f:
                img_bytes = f.read()
            try:
                os.remove(read_path)
            except Exception:
                pass
            return make_circle_avatar(img_bytes, radius)
        return make_default_avatar(radius)
    except Exception:
        try:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
        except Exception:
            pass
        return make_default_avatar(radius)


def build_couple_image(avatar1: Image.Image, avatar2: Image.Image) -> io.BytesIO:
    bg = Image.open(TEMPLATE_PATH).convert("RGBA")

    def paste_avatar(canvas, avatar, center, radius):
        x = center[0] - radius
        y = center[1] - radius
        canvas.paste(avatar, (x, y), avatar)

    paste_avatar(bg, avatar1, LEFT_CENTER,  LEFT_RADIUS)
    paste_avatar(bg, avatar2, RIGHT_CENTER, RIGHT_RADIUS)

    out = io.BytesIO()
    bg.convert("RGB").save(out, format="JPEG", quality=92)
    out.seek(0)
    return out


@app.on_message(filters.command("couple") & filters.group)
async def couple(client, msg: Message):
    try:
        await msg.delete()
    except Exception:
        pass

    chat_id = msg.chat.id
    loading = await client.send_message(chat_id, "💞 ᴀᴀᴊ ᴋᴀ ᴄᴏᴜᴘʟᴇ ᴅʜᴜɴᴅʜ ʀᴀʜᴀ ʜᴜɴ...")

    members = []
    try:
        async for member in client.get_chat_members(chat_id):
            u = member.user
            if u and not u.is_bot and not u.is_deleted:
                members.append(u)
    except ChatAdminRequired:
        await loading.delete()
        return await client.send_message(
            chat_id, "❌ <b>ʙᴏᴛ ᴋᴏ ᴀᴅᴍɪɴ ʙᴀɴᴀᴏ ᴘᴀʜʟᴇ!</b>"
        )
    except Exception as e:
        await loading.delete()
        return await client.send_message(
            chat_id, f"❌ <b>ᴇʀʀᴏʀ:</b> <code>{e}</code>"
        )

    if len(members) < 2:
        await loading.delete()
        return await client.send_message(
            chat_id,
            "❌ <b>ɪᴛɴᴇ ᴋᴀᴍ ᴍᴇᴍʙᴇʀs ʜᴀɪɴ? ᴄᴏᴜᴘʟᴇ ᴋᴀɪsᴇ ʙᴀɴᴇɢᴀ! 😂</b>",
        )

    p1, p2 = random.sample(members, 2)

    avatar1 = await get_user_avatar(client, p1.id, LEFT_RADIUS)
    avatar2 = await get_user_avatar(client, p2.id, RIGHT_RADIUS)

    try:
        image_buf = build_couple_image(avatar1, avatar2)
    except Exception as e:
        await loading.delete()
        return await client.send_message(
            chat_id, f"❌ Image error: <code>{e}</code>"
        )

    # html.escape — special chars se name toot na jaye
    name1     = html.escape(p1.first_name or "User")
    name2     = html.escape(p2.first_name or "User")
    chemistry = random.randint(60, 100)
    header    = random.choice(COUPLE_TEXTS)

    caption = (
        f"{header}\n\n"
        f"<a href='tg://user?id={p1.id}'>👦 {name1}</a>\n"
        f"        ❤️\n"
        f"<a href='tg://user?id={p2.id}'>👧 {name2}</a>\n\n"
        f"💫 ᴄʜᴇᴍɪsᴛʀʏ ➤ <b>{chemistry}%</b>\n"
        f"🌹 <i>ᴋɪsᴍᴀᴛ ɴᴇ ᴍɪʟᴀʏᴀ, ᴅɪʟ ɴᴇ ᴍᴀɴᴀʏᴀ</i>"
    )

    buttons = InlineKeyboardMarkup(
        [[InlineKeyboardButton("👑 Owner", url=f"https://t.me/{OWNER_USERNAME}")]]
    )

    await loading.delete()
    await client.send_photo(
        chat_id, photo=image_buf, caption=caption, reply_markup=buttons
    )
