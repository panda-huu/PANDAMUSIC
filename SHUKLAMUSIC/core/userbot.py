from pyrogram import Client
import config

assistants = []
assistantids = []


class Userbot:
    def __init__(self):
        self.one = Client(
            "ShuklaAssistant",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=config.STRING1,
        ) if config.STRING1 else None
        self.two = Client(
            "ShuklaAssistant2",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=config.STRING2,
        ) if config.STRING2 else None
        self.three = Client(
            "ShuklaAssistant3",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=config.STRING3,
        ) if config.STRING3 else None
        self.four = Client(
            "ShuklaAssistant4",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=config.STRING4,
        ) if config.STRING4 else None
        self.five = Client(
            "ShuklaAssistant5",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=config.STRING5,
        ) if config.STRING5 else None

    async def start(self):
        global assistants, assistantids
        for client in [self.one, self.two, self.three, self.four, self.five]:
            if client:
                await client.start()
                assistants.append(client)
                try:
                    me = await client.get_me()
                    assistantids.append(me.id)
                except:
                    pass

    async def stop(self):
        for client in [self.one, self.two, self.three, self.four, self.five]:
            if client:
                try:
                    await client.stop()
                except:
                    pass
