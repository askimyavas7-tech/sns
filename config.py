import re
import os
from os import getenv

from dotenv import load_dotenv
from pyrogram import filters

load_dotenv()

# Get this value from my.telegram.org/apps
API_ID = int(getenv("API_ID", "0"))
API_HASH = getenv("API_HASH", "")

API_URL = getenv("API_URL", "https://console.cloud.google.com")  # youtube song url
API_KEY = getenv("API_KEY", "AIzaSyD8kGqfpnVb_u3_AyyhNY_Ui6_iw-8rVPI")

# Get your token from @BotFather on Telegram.
BOT_TOKEN = getenv("BOT_TOKEN", "")

STICKER_ID = "CAACAgUAAxkBAAEObxloHODEbJMRLG0DgnPYJ7bOUXc5QwACmRkAAg6V6FSBJlu8dUgdCTYE"

# ✅ HATA DÜZELTİLDİ: getenv içine URL yazılmaz, ENV adı yazılır.
COOKIE_URL = getenv("COOKIE_URL", "https://batbin.me/minahassian")

# Get your mongo url from cloud.mongodb.com
MONGO_DB_URI = getenv("MONGO_DB_URI", "")
MUSIC_BOT_NAME = getenv("MUSIC_BOT_NAME", "")
PRIVATE_BOT_MODE = getenv("PRIVATE_BOT_MODE", "False")

DURATION_LIMIT_MIN = int(getenv("DURATION_LIMIT", "900"))

# Chat id of a group for logging bot's activities
LOGGER_ID = int(getenv("LOGGER_ID", "0"))

# Get this value from @BRANDRD_ROBOT on Telegram by /id
OWNER_ID = int(getenv("OWNER_ID", "0"))

## Fill these variables if you're deploying on heroku.
HEROKU_APP_NAME = getenv("HEROKU_APP_NAME", "")
HEROKU_API_KEY = getenv("HEROKU_API_KEY", "")

UPSTREAM_REPO = getenv("UPSTREAM_REPO", "https://github.com/zenaku16psp/sns")
UPSTREAM_BRANCH = getenv("UPSTREAM_BRANCH", "main")
GIT_TOKEN = getenv("GIT_TOKEN", None)

SUPPORT_CHANNEL_LINK = getenv("SUPPORT_CHANNEL_LINK", "https://t.me/MUHABBET_SOFASI_TR")
SUPPORT_CHAT_LINK = getenv("SUPPORT_CHAT_LINK", "https://t.me/MUHABBET_SOFASI_TR")

SUPPORT_CHANNEL = getenv("SUPPORT_CHANNEL", "https://t.me/MUHABBET_SOFASI_TR")
SUPPORT_CHAT = getenv("SUPPORT_CHAT", "https://t.me/MUHABBET_SOFASI_TR")

# ✅ HATA DÜZELTİLDİ: bool(getenv("False")) her zaman True döner. (string boş değil)
AUTO_LEAVING_ASSISTANT = getenv("AUTO_LEAVING_ASSISTANT", "False").lower() == "true"

# Auto Gcast/Broadcast Handler
AUTO_GCAST = os.getenv("AUTO_GCAST", "False").lower() == "true"
AUTO_GCAST_MSG = getenv("AUTO_GCAST_MSG", "")

SPOTIFY_CLIENT_ID = getenv("SPOTIFY_CLIENT_ID", "bcfe26b0ebc3428882a0b5fb3e872473")
SPOTIFY_CLIENT_SECRET = getenv("SPOTIFY_CLIENT_SECRET", "907c6a054c214005aeae1fd752273cc4")

SERVER_PLAYLIST_LIMIT = int(getenv("SERVER_PLAYLIST_LIMIT", "50"))
PLAYLIST_FETCH_LIMIT = int(getenv("PLAYLIST_FETCH_LIMIT", "25"))

SONG_DOWNLOAD_DURATION = int(getenv("SONG_DOWNLOAD_DURATION_LIMIT", "180"))
SONG_DOWNLOAD_DURATION_LIMIT = int(getenv("SONG_DOWNLOAD_DURATION_LIMIT", "2000"))

TG_AUDIO_FILESIZE_LIMIT = int(getenv("TG_AUDIO_FILESIZE_LIMIT", "104857600"))
TG_VIDEO_FILESIZE_LIMIT = int(getenv("TG_VIDEO_FILESIZE_LIMIT", "2097152000"))

STRING1 = getenv("STRING_SESSION",  None)
STRING2 = getenv("STRING_SESSION2", None)
STRING3 = getenv("STRING_SESSION3", None)
STRING4 = getenv("STRING_SESSION4", None)
STRING5 = getenv("STRING_SESSION5", None)

LOG = 2

# ✅ BANNED_USERS filters.user() yerine boş set olarak tutulmalı (liste/saklama için)
BANNED_USERS = set()

adminlist = {}
lyrical = {}
votemode = {}
autoclean = []
confirmer = {}

START_IMG_URL = getenv("START_IMG_URL", "https://files.catbox.moe/ama5e3.png")
PING_IMG_URL = getenv("PING_IMG_URL", "https://files.catbox.moe/ama5e3.png")
PLAYLIST_IMG_URL = "https://files.catbox.moe/ama5e3.png"
STATS_IMG_URL = "https://files.catbox.moe/ama5e3.png"
JOIN_IMG_URL = "https://files.catbox.moe/ama5e3.png"
TELEGRAM_AUDIO_URL = "https://files.catbox.moe/ama5e3.png"
TELEGRAM_VIDEO_URL = "https://files.catbox.moe/ama5e3.png"
STREAM_IMG_URL = "https://files.catbox.moe/ama5e3.png"
SOUNCLOUD_IMG_URL = "https://files.catbox.moe/ama5e3.png"
YOUTUBE_IMG_URL = "https://files.catbox.moe/ama5e3.png"
SPOTIFY_ARTIST_IMG_URL = "https://files.catbox.moe/ama5e3.png"
SPOTIFY_ALBUM_IMG_URL = "https://files.catbox.moe/ama5e3.png"
SPOTIFY_PLAYLIST_IMG_URL = "https://files.catbox.moe/ama5e3.png"


def time_to_seconds(time):
    stringt = str(time)
    try:
        return sum(int(x) * 60**i for i, x in enumerate(reversed(stringt.split(":"))))
    except Exception:
        return 0


DURATION_LIMIT = int(time_to_seconds(f"{DURATION_LIMIT_MIN}:00"))


if SUPPORT_CHANNEL:
    if not re.match(r"(?:http|https)://", SUPPORT_CHANNEL):
        raise SystemExit("[ERROR] - Your SUPPORT_CHANNEL url is wrong. Please ensure that it starts with https://")

if SUPPORT_CHAT:
    if not re.match(r"(?:http|https)://", SUPPORT_CHAT):
        raise SystemExit("[ERROR] - Your SUPPORT_CHAT url is wrong. Please ensure that it starts with https://")
