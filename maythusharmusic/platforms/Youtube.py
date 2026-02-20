import os
import yt_dlp
import requests
from pathlib import Path

# =====================================================
# ENV AYARLARI
# =====================================================

DEFAULT_FFMPEG = os.getenv("FFMPEG_LOCATION", "/usr/bin/ffmpeg")
COOKIES_URL = os.getenv("COOKIES_URL")
COOKIES_PATH = "cookies.txt"


# =====================================================
# COOKIES DOWNLOAD (URL'DEN)
# =====================================================

def download_cookies():
    if not COOKIES_URL:
        return None

    try:
        r = requests.get(COOKIES_URL, timeout=10)
        if r.status_code == 200:
            Path(COOKIES_PATH).write_text(r.text, encoding="utf-8")
            return COOKIES_PATH
        else:
            print("Cookies indirilemedi, status:", r.status_code)
    except Exception as e:
        print("Cookies hata:", e)

    return None


# =====================================================
# YDL OPTIONS (ULTRA STABLE)
# =====================================================

def get_ydl_opts(outtmpl: str, want_video: bool = False):
    cookies_file = download_cookies()

    ydl_opts = {
        # Format hatası vermemesi için en güvenli seçim
        "format": "bestvideo+bestaudio/best" if want_video else "bestaudio/best",

        "outtmpl": outtmpl,
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,

        # FFmpeg
        "ffmpeg_location": DEFAULT_FFMPEG,
        "merge_output_format": "mp4",
        "prefer_ffmpeg": True,

        # Anti 403
        "http_headers": {
            "User-Agent": "Mozilla/5.0"
        },

        # Stabilite
        "retries": 5,
        "fragment_retries": 5,
        "nocheckcertificate": True,
        "geo_bypass": True,
    }

    if cookies_file:
        ydl_opts["cookiefile"] = cookies_file

    return ydl_opts


# =====================================================
# DOWNLOAD FUNCTION
# =====================================================

def download(url: str, outtmpl: str, want_video: bool = False):
    ydl_opts = get_ydl_opts(outtmpl, want_video)

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info)
