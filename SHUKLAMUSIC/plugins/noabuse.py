# ---------------------------------------------------------------
# 🔸 RADHExMUSIC — noabuse.py
# 🔹 Auto-delete abusive messages | /noabuse on/off
# ---------------------------------------------------------------

import asyncio
import json
import os
import re

from pyrogram import filters
from pyrogram.enums import ChatMemberStatus
from pyrogram.types import Message

from SHUKLAMUSIC import app

# ── Persistent JSON file — bot restart hone par bhi toggle state bana rahega ──
_TOGGLE_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "noabuse_toggle_db.json")

def _load_toggles() -> dict:
    try:
        if os.path.exists(_TOGGLE_DB_PATH):
            with open(_TOGGLE_DB_PATH, "r") as f:
                return json.load(f)
    except Exception:
        pass
    return {}

def _save_toggles(data: dict):
    try:
        with open(_TOGGLE_DB_PATH, "w") as f:
            json.dump(data, f)
    except Exception:
        pass

def _key(chat_id: int) -> str:
    return str(chat_id)

def is_enabled(chat_id: int) -> bool:
    data = _load_toggles()
    return data.get(_key(chat_id), False)

def set_enabled(chat_id: int, value: bool):
    data = _load_toggles()
    data[_key(chat_id)] = value
    _save_toggles(data)

# ══════════════════════════════════════════════════════════════════════════════
# ROOT-BASED PATTERN (50 roots → 5000+ variations auto-cover)
# ══════════════════════════════════════════════════════════════════════════════
_ROOTS = [
    # Hindi roots
    "chut","bhosad","bhosd","bosd","lund","lund","lavd","lawd","gaand","gand",
    "rand","rund","madar","mader","behan","bhen","bhencho","behench",
    "haraam","haramz","kameen","rakhel","kasb","gashti","chinal","chhinaal",
    "jhaat","jhat","tatti","tattu","pesaab","pisaab","muth","mutth",
    "phudi","bur","chod","chodna","chodne","chodu",
    "suar","suwar","gadha","gadhi","ullu","kameena","nikamm","nalayak",
    "bhadwa","bhadwe","dalla","dalle","khanki","pataka",
    "hijra","hijda","chhakka","chakka","nalli","fattu","fuddu",
    "raand","raandi","rundi","randwa","randibaaz",
    # Punjabi roots
    "bhain","lun","maada","maadi","khabees","chudail",
    # English roots
    "fuck","fuk","fck","phuck","fcuk","fvck",
    "shit","sht","shyt",
    "bitch","biatch","bytch",
    "cunt","cnt",
    "dick","dik","dck",
    "cock","cok",
    "pussy","puss","pussi",
    "ass","ars","a55",
    "bastard","bastad",
    "whore","hore",
    "slut","slvt",
    "nigga","nigger","nigg",
    "motherfuck","motherf",
    "retard","retrd",
    "faggot","fagot","fag",
    "wank","wanker",
    "twat","tw4t",
    "prick","prik",
    "bollok","bollock",
]

_ROOT_PATTERN = re.compile(
    r"(?<![a-zA-Z0-9])(" +
    "|".join(re.escape(r) for r in sorted(set(_ROOTS), key=len, reverse=True)) +
    r")[a-zA-Z0-9]*(?![a-zA-Z0-9])",
    re.IGNORECASE,
)

# ══════════════════════════════════════════════════════════════════════════════
# EXACT WORD LIST (300+ unique real words & variations)
# ══════════════════════════════════════════════════════════════════════════════
RAW_WORDS = [
    # ── Hindi/Hinglish ────────────────────────────────────────────────────────
    "madarchod","madarcho","maderchod","madarchut","madarc","mc","m.c","m/c",
    "bhosdike","bhosdika","bhosdiki","bhosdi","bhosda","bhosd","bosdi","bosdike",
    "bhos","bhosad","bhosdiwale","bhosdiwali","bhosadwale","bhosadwali",
    "chutiya","chutiye","chutiyapa","chut","choot","chutad","chutmarike",
    "chutmar","chutmarke","ch*tiya","ch**iya","chootiya","chutyapa",
    "chutiyagiri","chutiyapon","chutiyap","chooti","choote",
    "lund","lode","loda","lavda","lavde","lavdi","laude","lauda","l*nd",
    "lundbaaz","lodu","lodi","lodon","lnda","lnde","lndi",
    "randi","rand","randwa","rundi","randa","randibaaz","raand","raandi",
    "harami","haramkhor","haraamzada","haramzada","haramzadi","haram",
    "haramzadey","haraamkhor","haraamzadi",
    "kamina","kamine","kameena","kameeni","kameenon","kaminey","kamini",
    "kutte","kutta","kutiya","kuti","kutti","kutton","kuttiya",
    "saala","saali","sala","sali","saale","saalaa","saalo",
    "behenchod","behench","behen","bc","b.c","behnchod","behan chod",
    "bhen ke","bhen ki","bhen ka","bhenchod","bhen ke lode","bhen ke laude",
    "bhenchodan","bhenchode","teri bhain","teri phen","teri bhen",
    "gandu","gaand","gaandu","gaand mara","gaand marwao","gaand ka","gaand ke",
    "gadha","gadhon","gadhi","gadhe","gadhon",
    "ullu","ulluke","ullu ke patthe","ullu ka pattha",
    "bhadwe","bhadwa","bhadwi","bhadwon","bhadwao",
    "chakke","chakka","chhakka","chhakke",
    "hijra","hijda","hijde","hijron","hijro",
    "maa ki","teri maa","maa ko","maa ke","maa chod","maa chuda",
    "teri maa ki","teri maa ka","teri maa ke","maa ki aankh",
    "teri behen","teri behen ki","teri behen ka",
    "teri gaand","teri gaand mein","teri gaand ka",
    "baap ko","baap ki","baap ka","tera baap","tere baap",
    "bur","bura chod","chinal","chhinaal","chhinaali",
    "muth maar","mutth","mutthal","muth maarle",
    "suvar","suwwar","suwar","suar","suwar ke","suar ke bacche",
    "nalli","nali","katwa","katwi","kattua","katue","katuo",
    "maagi","magi","maagi ke","maa gi",
    "bkl","bkll","bklll","bhkl","bkl ke","bklod","bkloda","bkll ke",
    "mkc","mkb","mkg",
    "teri naani","teri dadi","teri dadi ki","teri nani ki","teri bua ki",
    "chod","chodna","chodne","chodu","chodd","choda","chodi","chodke","chodkar",
    "gali","gaali","gaaliyan","gaaliya",
    "jhatu","jhaatu","jhat","jhaat","jhaant","jhatu sa",
    "tatti","tattu","tattar","tatpatti","tatte",
    "pisab","pissab","peshab","pesaab",
    "patakha","fattu","fatte","fuddu","fuddhu",
    "nikamma","nikaama","nikammi","nikamme",
    "nalayak","nalaayak","nalayak insaan",
    "raand","raandi","raanda",
    "maakichut","maakibur","maakigaand",
    "bsdk","bsdke","bsdki","bsdkwale","bsdk ke",
    "lodu","lodi","lode","lodon","lodeo",
    "choot","choote","chooti","chooton",
    "teri phudi","phudi","phuddi","phudda",
    "kamine","kamini","kaminey","kamino",
    "bawasir","bawaseer","bawasiri",
    "chhakka","chhakke","chakku",
    "rakhel","rakhail","rakhelin",
    "kasbi","kasbe","kasbiya","kasbiyon",
    "dalle","dalla","dalli","dallon","dallon ke",
    "khanki","khankiya","khanke","khankon",
    "gashti","gashtiya","gashtiyon",
    "pataka","patake","pataki",
    "chikna","chikne","chikni","chikno",
    "maal","randi maal","maal hai",
    "bhadwa","bhadwe","bhadwi",
    "kutti","kutton","kuttiya","kutte ki aulad",
    "haramkhor","haramkhoron","harami log",
    "sali randi","saali randi","saali kameeni",
    "teri maa ka","teri maa ki aankh","teri maa ki",
    "maa chudao","maa ka","maa ke liye",
    "behen ke takke","behen ke","behen ki kasam nahi",
    "gaand maar","gaand mein","gaand phad","gaand fat",
    "lund muh mein","lund le","lund ka","lund ki",
    "chut mein","chut le","chut ka dhakkan",
    "randi ki aulad","rand ki","rand ke",
    "harami ki aulad","harami log","harami kahin ke",
    "kutte kahin ke","kuttiya kahin ki",
    "gadhe kahin ke","gadhe ki aulad",
    "ullu kahin ke","ullu ki aulad",
    "bhosad ke","bhosad mein","bhosad wale",
    "madar ke","madar chod","maderchod",
    "teri maa ko","teri maa ne","teri maa wali",
    "bhen ke lode","bhen ke takke","bhen ke",
    "randi baaz","rand baaz","harami baaz",
    "lund choos","lund choosna","lund choosti",
    "gaand chaat","gaand chaatna","gaand chaate",
    "tatti kha","tatti khao","tatti khana",
    "pisaab pi","pisaab peena","pisaab piyo",
    "jhaat ke","jhaat wale","jhaat mein",
    "fuddu kahin ke","fattu kahin ka",
    "nikamma kahin ka","nalayak kahin ka",
    # Punjabi
    "maada","maadi","maade","teri maa di","teri maa de",
    "kure","kuria","kuri","kutte di maa","kutiye",
    "teri bhain di","teri bhain de","teri phen di",
    "lun de","teri phen de lun","lun le",
    "khabees","khabeesa","khabeesi","khabeesan",
    "chudail","chudaail","chudayla","chudailon",
    "kuttiye","kuttiya","kuttian",
    "haram da","haram di","haramdi",
    "bhen di","bhen da","bhen de",
    "gandu punjabi","gand pa","gand mara",
    # English
    "fuck","fucker","fuckers","fucking","fucked","fuckoff","fuckup",
    "fuck you","f*ck","f**k","fck","fuk","fucc","fvck","phuck","fcuk",
    "motherfucker","motherf","mf","mofo","mfker",
    "shit","shitty","bullshit","sh*t","shyt","sht","shite","shiit",
    "bastard","bitch","bitches","b*tch","biatch","bytch","b1tch","b!tch",
    "whore","slut","slutty","wh*re","sl*t","whor3","sl**",
    "cunt","c*nt","cnt","c**t",
    "dick","d*ck","dck","dik","d!ck","d1ck",
    "cock","c*ck","cok","c0ck",
    "pussy","p*ssy","puss","pu$$y","pu55y","pussi",
    "asshole","a**hole","a**","arse","ass","a55","@ss","a$s","@$$",
    "nigga","nigger","n*gga","n*gger","nigg","n1gga","n1gger",
    "retard","retarded","ret*rd","ret4rd",
    "idiot","stupid","dumbass","dumba**","dumb fuck",
    "wtf","stfu","gtfo","kys","kms",
    "prick","pr*ck","prik",
    "wanker","w*nker","wank","w@nker",
    "twat","tw*t","tw4t",
    "bollocks","b*llocks","bollock",
    "faggot","f*ggot","fag","f4ggot","fagg0t",
    "cracker","cr*cker",
    "spastic","sp*stic",
    "b*stard","ba5tard","b@stard",
    "son of a bitch","sob","s.o.b",
    "piece of shit","pos","p.o.s",
    "go to hell","go fuck yourself","gfy",
    "eat shit","kiss my ass","kma",
    "douchebag","douche","d-bag",
    "scumbag","scum","sc*m",
    "jackass","jack ass","j@ckass",
    "dipshit","dip shit","dips**t",
    "shithead","shit head","sh*thead",
    "asswipe","ass wipe","@sswipe",
    "butthead","butt head",
    "cum","cumshot","c*m","c**",
    "boner","b*ner",
    "titties","tits","t*ts","t1ts",
    "boobs","b**bs","b00bs",
    "nude","nudes","n*de",
    "porn","p*rn","pr0n","p0rn",
    "rape","r*pe","raped","raping","rapist",
    "molest","molestation",
    "pedophile","pedo","p*do",
    "sex","s*x","s3x","sexx",
    "sexy","s*xy","sexxy",
    "horny","h*rny","hornyyy",
    # Leet/bypass forms
    "ch4t","ch@t","lund@","l0de","l0da","b0sd","bh0sd",
    "fuk","fvk","phuk","f_ck","fu*k",
    "sh1t","$hit","5hit","$h1t",
    "b1tch","b!tch","b*tch",
    "d!ck","d1ck","d*ck",
    "p*ssy","pu$$y","pu55y",
    "m@darchod","m@darc","mad@rchod",
    "chut!ya","chut1ya","ch*tiya","chut@ya",
    "g@and","g4and","g@@nd",
    "r@ndi","r4ndi","r@nd",
    "h@rami","har@mi","h4rami",
    "bh0sdi","bh@sdi","bhos@di",
    "lund@","l*nd","l@uda","l@vda",
    "k@meena","kam33na","k4meena",
    "s@la","s4la","s@ali","s4ali",
    "bc","b.c","b/c","b*c",
    "mc","m.c","m/c","m*c",
    "bkl","b.k.l","b/k/l",
]

# ══════════════════════════════════════════════════════════════════════════════
# COMBINED DETECTION — root pattern + exact words
# ══════════════════════════════════════════════════════════════════════════════
_EXACT_PATTERN = re.compile(
    r"(?<![a-zA-Z0-9])(" +
    "|".join(re.escape(w) for w in sorted(set(RAW_WORDS), key=len, reverse=True)) +
    r")(?![a-zA-Z0-9])",
    re.IGNORECASE,
)

def _normalize(text: str) -> str:
    # Remove zero-width chars
    text = re.sub(r"[\u200b-\u200f\u202a-\u202e\uFEFF]", "", text)
    # Normalize spaces
    text = re.sub(r"\s+", " ", text).strip()
    # Common leet substitutions
    text = text.replace("@", "a").replace("0", "o").replace("1", "i")
    text = text.replace("3", "e").replace("4", "a").replace("5", "s")
    text = text.replace("$", "s").replace("+", "t").replace("!", "i")
    return text

def contains_abuse(text: str) -> bool:
    if not text:
        return False
    clean = _normalize(text)
    # Check root pattern first (faster for most cases)
    if _ROOT_PATTERN.search(clean):
        return True
    # Then exact list
    if _EXACT_PATTERN.search(clean):
        return True
    return False


# ── /noabuse on/off ───────────────────────────────────────────────────────────
@app.on_message(filters.command("noabuse") & filters.group)
async def noabuse_cmd(client, msg: Message):
    try:
        await msg.delete()
    except Exception:
        pass
    member = await client.get_chat_member(msg.chat.id, msg.from_user.id)
    if member.status not in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER):
        return await msg.reply("❌ <b>ꜱɪʀꜰ ᴀᴅᴍɪɴ ɪsᴛᴇᴍᴀᴀʟ ᴋᴀʀ ꜱᴀᴋᴛᴇ ʜᴀɪɴ!</b>")

    args = msg.command
    if len(args) < 2 or args[1].lower() not in ("on", "off"):
        status = "✅ ᴏɴ" if is_enabled(msg.chat.id) else "❌ ᴏꜰꜰ"
        return await msg.reply(
            f"<b>🚫 ɴᴏ-ᴀʙᴜꜱᴇ ꜱᴛᴀᴛᴜꜱ:</b> {status}\n\n"
            f"➻ /noabuse on  — ᴇɴᴀʙʟᴇ ✅\n"
            f"➻ /noabuse off — ᴅɪꜱᴀʙʟᴇ ❌"
        )

    action = args[1].lower()
    if action == "on":
        set_enabled(msg.chat.id, True)
        await msg.reply(
            "✅ <b>ɴᴏ-ᴀʙᴜꜱᴇ ᴍᴏᴅᴇ ᴇɴᴀʙʟᴇᴅ!</b>\n\n"
            "🛡 ᴀʙ ꜱᴇ ʜᴀʀ ɢᴀʟɪ ᴀᴜᴛᴏ-ᴅᴇʟᴇᴛᴇ ʜᴏɢɪ — ᴀᴅᴍɪɴ ʜᴏ ʏᴀ ɴᴀ ʜᴏ 🚫"
        )
    else:
        set_enabled(msg.chat.id, False)
        await msg.reply("❌ <b>ɴᴏ-ᴀʙᴜꜱᴇ ᴍᴏᴅᴇ ᴅɪꜱᴀʙʟᴇᴅ!</b>")


# ── Blacklist DB reader ───────────────────────────────────────────────────────
_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "blacklist_db.json")

def _get_custom_words(chat_id: int) -> list:
    try:
        if os.path.exists(_DB_PATH):
            with open(_DB_PATH, "r") as f:
                data = json.load(f)
            return data.get(str(chat_id), [])
    except Exception:
        pass
    return []

def _matches_custom(text: str, words: list) -> bool:
    if not text or not words:
        return False
    t = text.lower()
    for w in words:
        if re.search(r"(?<![a-zA-Z0-9])" + re.escape(w) + r"(?![a-zA-Z0-9])", t):
            return True
    return False


# ── Auto-detect & delete ──────────────────────────────────────────────────────
@app.on_message(filters.group & filters.text, group=-1)
async def abuse_watcher(client, msg: Message):
    if not msg.from_user:
        return

    text = msg.text or msg.caption or ""

    builtin_hit = is_enabled(msg.chat.id) and contains_abuse(text)
    custom_words = _get_custom_words(msg.chat.id)
    custom_hit   = _matches_custom(text, custom_words)

    if not builtin_hit and not custom_hit:
        return

    try:
        await msg.delete()
    except Exception as e:
        # Yahi print dikhayega asli wajah — mostly bot admin nahi hai
        # ya usko "Delete Messages" permission nahi mili group me.
        print(f"[NOABUSE] Delete failed in chat {msg.chat.id}: {e}", flush=True)
        return

    try:
        warn = await client.send_message(
            msg.chat.id,
            f"⚠️ {msg.from_user.mention}\n\n"
            "<b>ᴅᴏɴ'ᴛ ᴜꜱᴇ ᴀʙᴜꜱɪᴠᴇ ᴡᴏʀᴅꜱ ɪɴ ɢʀᴏᴜᴘ!</b>",
        )
        await asyncio.sleep(6)
        await warn.delete()
    except Exception as e:
        print(f"[NOABUSE] Warn message failed in chat {msg.chat.id}: {e}", flush=True)
