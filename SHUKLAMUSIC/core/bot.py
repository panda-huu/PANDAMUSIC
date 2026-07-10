from pyrogram import Client
import config

class SHUKLA(Client):
    def __init__(self):
        super().__init__(
            "ShuklaBot",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            bot_token=config.BOT_TOKEN,
            plugins=dict(root="SHUKLAMUSIC/plugins"),
        )
