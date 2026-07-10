from SHUKLAMUSIC.core.bot import SHUKLA
from SHUKLAMUSIC.core.userbot import Userbot
from SHUKLAMUSIC.misc import dbb
from .logging import LOGGER

dbb()

app = SHUKLA()
userbot = Userbot()

from .platforms import *

Apple      = AppleAPI()
Carbon     = CarbonAPI()
SoundCloud = SoundAPI()
Spotify    = SpotifyAPI()
Resso      = RessoAPI()
Telegram   = TeleAPI()
YouTube    = YouTubeAPI()
