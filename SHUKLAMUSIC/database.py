"""
SHUKLAMUSIC — PostgreSQL Database Layer (asyncpg + Supabase)
-------------------------------------------------------------
Persistent storage for users, chats, auth, bans, lang, etc.

Setup:
  1. config.py mein DATABASE_URL daalo
  2. pip install asyncpg
  3. bot start hone pe init_db() auto-call hoga
"""

import asyncio
import asyncpg
from typing import List

import config
from SHUKLAMUSIC.logging import LOGGER

log = LOGGER(__name__)

_pool: asyncpg.Pool = None


# ══════════════════════════════════════════════════════════════════════════════
#  POOL INIT + TABLE CREATE
# ══════════════════════════════════════════════════════════════════════════════

async def init_db():
    global _pool
    try:
        from urllib.parse import urlparse
        url = urlparse(config.DATABASE_URL)
        _pool = await asyncpg.create_pool(
            host=url.hostname,
            port=int(url.port) if url.port else 5432,
            user=url.username,
            password=config.DATABASE_PASSWORD,
            database=url.path.lstrip("/"),
            min_size=2,
            max_size=10,
            command_timeout=30,
            ssl="require",
            statement_cache_size=0,
        )
        await _create_tables()
        log.info("✅ Supabase PostgreSQL connected!")
    except Exception as e:
        log.error(f"❌ DB connection failed: {e}")
        _pool = None


async def _create_tables():
    async with _pool.acquire() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS served_users (
                user_id BIGINT PRIMARY KEY,
                added_at TIMESTAMPTZ DEFAULT NOW()
            );

            CREATE TABLE IF NOT EXISTS served_chats (
                chat_id BIGINT PRIMARY KEY,
                added_at TIMESTAMPTZ DEFAULT NOW()
            );

            CREATE TABLE IF NOT EXISTS lang_settings (
                chat_id BIGINT PRIMARY KEY,
                lang TEXT DEFAULT 'en'
            );

            CREATE TABLE IF NOT EXISTS auth_users (
                chat_id BIGINT NOT NULL,
                user_id BIGINT NOT NULL,
                added_by BIGINT,
                PRIMARY KEY (chat_id, user_id)
            );

            CREATE TABLE IF NOT EXISTS banned_users (
                user_id BIGINT PRIMARY KEY,
                reason TEXT DEFAULT '',
                banned_at TIMESTAMPTZ DEFAULT NOW()
            );

            CREATE TABLE IF NOT EXISTS gbanned_users (
                user_id BIGINT PRIMARY KEY,
                banned_at TIMESTAMPTZ DEFAULT NOW()
            );

            CREATE TABLE IF NOT EXISTS blacklisted_chats (
                chat_id BIGINT PRIMARY KEY
            );

            CREATE TABLE IF NOT EXISTS playmode (
                chat_id BIGINT PRIMARY KEY,
                mode TEXT DEFAULT 'Direct'
            );
        """)
    log.info("✅ Tables ready")


def _pool_ok() -> bool:
    return _pool is not None


# ══════════════════════════════════════════════════════════════════════════════
#  SERVED USERS
# ══════════════════════════════════════════════════════════════════════════════

async def add_served_user(user_id: int):
    if not _pool_ok(): return
    try:
        async with _pool.acquire() as conn:
            await conn.execute(
                "INSERT INTO served_users(user_id) VALUES($1) ON CONFLICT DO NOTHING",
                user_id,
            )
    except Exception as e:
        log.warning(f"add_served_user: {e}")


async def get_served_users() -> List[dict]:
    if not _pool_ok(): return []
    try:
        async with _pool.acquire() as conn:
            rows = await conn.fetch("SELECT user_id FROM served_users")
            return [{"user_id": r["user_id"]} for r in rows]
    except Exception as e:
        log.warning(f"get_served_users: {e}")
        return []


# ══════════════════════════════════════════════════════════════════════════════
#  SERVED CHATS
# ══════════════════════════════════════════════════════════════════════════════

async def add_served_chat(chat_id: int):
    if not _pool_ok(): return
    try:
        async with _pool.acquire() as conn:
            await conn.execute(
                "INSERT INTO served_chats(chat_id) VALUES($1) ON CONFLICT DO NOTHING",
                chat_id,
            )
    except Exception as e:
        log.warning(f"add_served_chat: {e}")


async def get_served_chats() -> List[dict]:
    if not _pool_ok(): return []
    try:
        async with _pool.acquire() as conn:
            rows = await conn.fetch("SELECT chat_id FROM served_chats")
            return [{"chat_id": r["chat_id"]} for r in rows]
    except Exception as e:
        log.warning(f"get_served_chats: {e}")
        return []


# ══════════════════════════════════════════════════════════════════════════════
#  LANGUAGE
# ══════════════════════════════════════════════════════════════════════════════

_lang_cache: dict = {}

async def get_lang(chat_id: int) -> str:
    if chat_id in _lang_cache:
        return _lang_cache[chat_id]
    if not _pool_ok(): return "en"
    try:
        async with _pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT lang FROM lang_settings WHERE chat_id=$1", chat_id
            )
            lang = row["lang"] if row else "en"
            _lang_cache[chat_id] = lang
            return lang
    except Exception:
        return "en"


async def set_lang(chat_id: int, lang: str):
    _lang_cache[chat_id] = lang
    if not _pool_ok(): return
    try:
        async with _pool.acquire() as conn:
            await conn.execute(
                """INSERT INTO lang_settings(chat_id, lang) VALUES($1,$2)
                   ON CONFLICT(chat_id) DO UPDATE SET lang=EXCLUDED.lang""",
                chat_id, lang,
            )
    except Exception as e:
        log.warning(f"set_lang: {e}")


# ══════════════════════════════════════════════════════════════════════════════
#  AUTH USERS
# ══════════════════════════════════════════════════════════════════════════════

async def add_auth_user(chat_id: int, user_id: int, added_by: int = 0):
    if not _pool_ok(): return
    try:
        async with _pool.acquire() as conn:
            await conn.execute(
                """INSERT INTO auth_users(chat_id, user_id, added_by)
                   VALUES($1,$2,$3) ON CONFLICT DO NOTHING""",
                chat_id, user_id, added_by,
            )
    except Exception as e:
        log.warning(f"add_auth_user: {e}")


async def remove_auth_user(chat_id: int, user_id: int):
    if not _pool_ok(): return
    try:
        async with _pool.acquire() as conn:
            await conn.execute(
                "DELETE FROM auth_users WHERE chat_id=$1 AND user_id=$2",
                chat_id, user_id,
            )
    except Exception as e:
        log.warning(f"remove_auth_user: {e}")


async def get_auth_users(chat_id: int) -> List[int]:
    if not _pool_ok(): return []
    try:
        async with _pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT user_id FROM auth_users WHERE chat_id=$1", chat_id
            )
            return [r["user_id"] for r in rows]
    except Exception as e:
        log.warning(f"get_auth_users: {e}")
        return []


async def is_auth_user(chat_id: int, user_id: int) -> bool:
    return user_id in await get_auth_users(chat_id)


# ══════════════════════════════════════════════════════════════════════════════
#  BANNED USERS
# ══════════════════════════════════════════════════════════════════════════════

async def ban_user(user_id: int, reason: str = ""):
    if not _pool_ok(): return
    try:
        async with _pool.acquire() as conn:
            await conn.execute(
                """INSERT INTO banned_users(user_id, reason) VALUES($1,$2)
                   ON CONFLICT(user_id) DO UPDATE SET reason=EXCLUDED.reason""",
                user_id, reason,
            )
    except Exception as e:
        log.warning(f"ban_user: {e}")


async def unban_user(user_id: int):
    if not _pool_ok(): return
    try:
        async with _pool.acquire() as conn:
            await conn.execute(
                "DELETE FROM banned_users WHERE user_id=$1", user_id
            )
    except Exception as e:
        log.warning(f"unban_user: {e}")


async def is_banned_user(user_id: int) -> bool:
    if not _pool_ok(): return False
    try:
        async with _pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT 1 FROM banned_users WHERE user_id=$1", user_id
            )
            return row is not None
    except Exception:
        return False


async def get_banned_users() -> List[int]:
    if not _pool_ok(): return []
    try:
        async with _pool.acquire() as conn:
            rows = await conn.fetch("SELECT user_id FROM banned_users")
            return [r["user_id"] for r in rows]
    except Exception:
        return []


# ══════════════════════════════════════════════════════════════════════════════
#  GLOBALLY BANNED USERS
# ══════════════════════════════════════════════════════════════════════════════

async def gban_user(user_id: int):
    if not _pool_ok(): return
    try:
        async with _pool.acquire() as conn:
            await conn.execute(
                "INSERT INTO gbanned_users(user_id) VALUES($1) ON CONFLICT DO NOTHING",
                user_id,
            )
    except Exception as e:
        log.warning(f"gban_user: {e}")


async def ungban_user(user_id: int):
    if not _pool_ok(): return
    try:
        async with _pool.acquire() as conn:
            await conn.execute(
                "DELETE FROM gbanned_users WHERE user_id=$1", user_id
            )
    except Exception as e:
        log.warning(f"ungban_user: {e}")


async def get_gbanned() -> List[int]:
    if not _pool_ok(): return []
    try:
        async with _pool.acquire() as conn:
            rows = await conn.fetch("SELECT user_id FROM gbanned_users")
            return [r["user_id"] for r in rows]
    except Exception:
        return []


# ══════════════════════════════════════════════════════════════════════════════
#  BLACKLISTED CHATS
# ══════════════════════════════════════════════════════════════════════════════

async def blacklist_chat(chat_id: int):
    if not _pool_ok(): return
    try:
        async with _pool.acquire() as conn:
            await conn.execute(
                "INSERT INTO blacklisted_chats(chat_id) VALUES($1) ON CONFLICT DO NOTHING",
                chat_id,
            )
    except Exception as e:
        log.warning(f"blacklist_chat: {e}")


async def unblacklist_chat(chat_id: int):
    if not _pool_ok(): return
    try:
        async with _pool.acquire() as conn:
            await conn.execute(
                "DELETE FROM blacklisted_chats WHERE chat_id=$1", chat_id
            )
    except Exception as e:
        log.warning(f"unblacklist_chat: {e}")


async def blacklisted_chats() -> set:
    if not _pool_ok(): return set()
    try:
        async with _pool.acquire() as conn:
            rows = await conn.fetch("SELECT chat_id FROM blacklisted_chats")
            return {r["chat_id"] for r in rows}
    except Exception:
        return set()


# ══════════════════════════════════════════════════════════════════════════════
#  PLAYMODE
# ══════════════════════════════════════════════════════════════════════════════

async def get_playmode(chat_id: int) -> str:
    if not _pool_ok(): return "Direct"
    try:
        async with _pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT mode FROM playmode WHERE chat_id=$1", chat_id
            )
            return row["mode"] if row else "Direct"
    except Exception:
        return "Direct"


async def set_playmode(chat_id: int, mode: str):
    if not _pool_ok(): return
    try:
        async with _pool.acquire() as conn:
            await conn.execute(
                """INSERT INTO playmode(chat_id, mode) VALUES($1,$2)
                   ON CONFLICT(chat_id) DO UPDATE SET mode=EXCLUDED.mode""",
                chat_id, mode,
            )
    except Exception as e:
        log.warning(f"set_playmode: {e}")


# ══════════════════════════════════════════════════════════════════════════════
#  SUDOERS (config se, DB mein nahi)
# ══════════════════════════════════════════════════════════════════════════════

async def get_sudoers() -> List[int]:
    return [config.OWNER_ID]
