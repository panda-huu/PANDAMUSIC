import time
from pyrogram import filters
import config
from .logging import LOGGER

# ── Boot timestamp ────────────────────────────────────────────────────────────
_boot_: float = time.time()

# ── In-memory queue DB — at module level so `from misc import db` works ───────
db: dict = {}

# ── Sudo users — SET, not filters.user() (stats.py uses `in` and `len`) ──────
SUDOERS: set = set()

mongodb = None  # stub — no MongoDB


def dbb():
    db.clear()           # DO NOT do db = {} — that breaks imported references
    SUDOERS.add(config.OWNER_ID)
    LOGGER(__name__).info("Database loaded (in-memory)")


async def sudo():
    SUDOERS.add(config.OWNER_ID)
    LOGGER(__name__).info("Sudo users loaded")
