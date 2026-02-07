import asyncio
import os
import re
import json
from typing import Union

import yt_dlp
# import requests  <-- ဖယ်ရှားလိုက်ပါပြီ (API မသုံးတော့လို့)
from pyrogram.enums import MessageEntityType
from pyrogram.types import Message
from youtubesearchpython.__future__ import VideosSearch

# --- Database Import (Cache function များ ဖယ်ရှားပြီး) ---
from maythusharmusic.utils.database import is_on_off
from maythusharmusic.utils.formatters import time_to_seconds

import glob
import random
import logging
import aiohttp 

# Logger ကို သတ်မှတ်ခြင်း
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- API KEYS နှင့် BASE URL များ ဖယ်ရှားလိုက်ပါပြီ ---

_cookies_warned = False

def extract_video_id(link: str) -> str:
    patterns = [
        r'youtube\.com\/(?:embed\/|v\/|watch\?v=|watch\?.+&v=)([0-9A-Za-z_-]{11})',
        r'youtu\.be\/([0-9A-Za-z_-]{11})',
        r'youtube\.com\/(?:playlist\?list=[^&]+&v=|v\/)([0-9A-Za-z_-]{11})',
        r'youtube\.com\/(?:.*\?v=|.*\/)([0-9A-Za-z_-]{11})'
    ]

    for pattern in patterns:
        match = re.search(pattern, link)
        if match:
            return match.group(1)

    raise ValueError("Invalid YouTube link provided.")

def get_cookies():
    """
    သတ်မှတ်ထားသော cookies.txt ဖိုင်၏ path ကို ပြန်ပေးသည်။
    """
    global _cookies_warned
    cookie_path = "maythusharmusic/cookies/cookies.txt"
    
    if not os.path.exists(cookie_path):
        if not _cookies_warned:
            _cookies_warned = True
            logger.warning(f"{cookie_path} ကို ရှာမတွေ့ပါ၊ download များ မအောင်မြင်နိုင်ပါ။")
        return None
        
    return cookie_path

async def save_cookies(urls: list[str]) -> None:
    """
    ပေးလာသော URL များထဲမှ ပထမဆုံး URL မှ cookie ကို cookies.txt တွင် သိမ်းဆည်းသည်။
    """
    if not urls:
        logger.warning("save_cookies သို့ URL များ ပေးပို့မထားပါ။")
        return
    
    logger.info("ပထမဆုံး URL မှ cookie ကို cookies.txt တွင် သိမ်းဆည်းနေပါသည်...")
    url = urls[0]
    path = "maythusharmusic/cookies/cookies.txt"
    link = url.replace("me/", "me/raw/")
    
    os.makedirs(os.path.dirname(path), exist_ok=True)
        
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(link) as resp:
                if resp.status == 200:
                    with open(path, "wb") as fw:
                        fw.write(await resp.read())
                    logger.info("Cookie များကို cookies.txt တွင် အောင်မြင်စွာ သိမ်းဆည်းပြီးပါပြီ။")
                else:
                    logger.error(f"{link} မှ cookie download လုပ်ရာတွင် မအောင်မြင်ပါ၊ status: {resp.status}")
    except Exception as e:
        logger.error(f"Cookie သိမ်းဆည်းရာတွင် အမှားအယွင်း ဖြစ်ပွားပါသည်: {e}")


async def check_file_size(link):
    async def get_format_info(link):
        cookie_file = get_cookies() 
        proc_args = ["yt-dlp", "-J"]
        if cookie_file:
            proc_args.extend(["--cookies", cookie_file])
        proc_args.append(link)

        proc = await asyncio.create_subprocess_exec(
            *proc_args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        if proc.returncode != 0:
            print(f'Error:\n{stderr.decode()}')
            return None
        return json.loads(stdout.decode())

    def parse_size(formats):
        total_size = 0
        for format in formats:
            if 'filesize' in format:
                total_size += format['filesize']
        return total_size

    info = await get_format_info(link)
    if info is None:
        return None
    
    formats = info.get('formats', [])
    if not formats:
        print("No formats found.")
        return None
    
    total_size = parse_size(formats)
    return total_size


async def shell_cmd(cmd):
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    out, errorz = await proc.communicate()
    if errorz:
        if "unavailable videos are hidden" in (errorz.decode("utf-8")).lower():
            return out.decode("utf-8")
        else:
            return errorz.decode("utf-8")
    return out.decode("utf-8")


class YouTubeAPI:
    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.regex = r"(?:youtube\.com|youtu\.be)"
        self.status = "https://www.youtube.com/oembed?url="
        self.listbase = "https://youtube.com/playlist?list="
        self.reg = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
        # Cache dictionary ကို ဖယ်ရှားလိုက်ပါပြီ

    async def exists(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if re.search(self.regex, link):
            return True
        else:
            return False

    async def url(self, message_1: Message) -> Union[str, None]:
        messages = [message_1]
        if message_1.reply_to_message:
            messages.append(message_1.reply_to_message)
        text = ""
        offset = None
        length = None
        for message in messages:
            if offset:
                break
            if message.entities:
                for entity in message.entities:
                    if entity.type == MessageEntityType.URL:
                        text = message.text or message.caption
                        offset, length = entity.offset, entity.length
                        break
            elif message.caption_entities:
                for entity in message.caption_entities:
                    if entity.type == MessageEntityType.TEXT_LINK:
                        return entity.url
        if offset in (None,):
            return None
        return text[offset : offset + length]

    # --- Cleaned Fetch Functions (No Caching) ---

    async def _fetch_from_youtube(self, link: str):
        """
        YouTube မှ Direct ရှာဖွေခြင်း (Cache သိမ်းဆည်းမှု မပါဝင်တော့ပါ)
        """
        results = VideosSearch(link, limit=1)
        try:
            result = (await results.next())["result"][0]
        except IndexError:
            logger.error(f"YouTube မှာ {link} ကို ရှာမတွေ့ပါ။")
            return None

        title = result["title"]
        duration_min = result["duration"]
        thumbnail = result["thumbnails"][0]["url"].split("?")[0]
        vidid = result["id"]
        yturl = result["link"]

        if str(duration_min) == "None":
            duration_sec = 0
        else:
            duration_sec = int(time_to_seconds(duration_min))
            
        video_details = {
            "title": title,
            "duration_min": duration_min,
            "duration_sec": duration_sec,
            "thumbnail": thumbnail,
            "vidid": vidid,
            "link": yturl,
        }
        
        return video_details

    async def _get_video_details(self, link: str, videoid: Union[bool, str] = None):
        """
        Cache စစ်ဆေးမှုများကို ဖယ်ရှားပြီး Direct Fetch ကိုသာ ခေါ်ပါမည်။
        """
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]

        # Cache စစ်ဆေးမှုများကို ကျော်ပြီးတိုက်ရိုက်ရှာပါ
        return await self._fetch_from_youtube(link)


    async def details(self, link: str, videoid: Union[bool, str] = None):
        details = await self._get_video_details(link, videoid)
        if not details:
            return None, None, 0, None, None
            
        return (
            details["title"],
            details["duration_min"],
            details["duration_sec"],
            details["thumbnail"],
            details["vidid"],
        )

    async def title(self, link: str, videoid: Union[bool, str] = None):
        details = await self._get_video_details(link, videoid)
        return details["title"] if details else "Unknown Title"

    async def duration(self, link: str, videoid: Union[bool, str] = None):
        details = await self._get_video_details(link, videoid)
        return details["duration_min"] if details else "00:00"

    async def thumbnail(self, link: str, videoid: Union[bool, str] = None):
        details = await self._get_video_details(link, videoid)
        return details["thumbnail"] if details else None

    async def track(self, link: str, videoid: Union[bool, str] = None):
        details = await self._get_video_details(link, videoid)
        if not details:
            return {}, None
            
        track_details = {
            "title": details["title"],
            "link": details["link"],
            "vidid": details["vidid"],
            "duration_min": details["duration_min"],
            "thumb": details["thumbnail"],
        }
        return track_details, details["vidid"]

    # --- End Details Functions ---

    async def video(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        proc = await asyncio.create_subprocess_exec(
            "yt-dlp",
            "-g",
            "-f",
            "best[height<=?720][width<=?1280]",
            f"{link}",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()
        if stdout:
            return 1, stdout.decode().split("\n")[0]
        else:
            return 0, stderr.decode()

    async def playlist(self, link, limit, user_id, videoid: Union[bool, str] = None):
        if videoid:
            link = self.listbase + link
        if "&" in link:
            link = link.split("&")[0]
        playlist = await shell_cmd(
            f"yt-dlp -i --get-id --flat-playlist --playlist-end {limit} --skip-download {link}"
        )
        try:
            result = playlist.split("\n")
            for key in result:
                if key == "":
                    result.remove(key)
        except:
            result = []
        return result

    async def formats(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        ytdl_opts = { "quiet": True } 
        ydl = yt_dlp.YoutubeDL(ytdl_opts)
        with ydl:
            formats_available = []
            r = ydl.extract_info(link, download=False)
            for format in r["formats"]:
                try:
                    str(format["format"])
                except:
                    continue
                if not "dash" in str(format["format"]).lower():
                    try:
                        format["format"]
                        format["filesize"]
                        format["format_id"]
                        format["ext"]
                        format["format_note"]
                    except:
                        continue
                    formats_available.append(
                        {
                            "format": format["format"],
                            "filesize": format["filesize"],
                            "format_id": format["format_id"],
                            "ext": format["ext"],
                            "format_note": format["format_note"],
                            "yturl": link,
                        }
                    )
            return formats_available, link

    async def slider(
        self,
        link: str,
        query_type: int,
        videoid: Union[bool, str] = None,
    ):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        a = VideosSearch(link, limit=10)
        result = (await a.next()).get("result")
        title = result[query_type]["title"]
        duration_min = result[query_type]["duration"]
        vidid = result[query_type]["id"]
        thumbnail = result[query_type]["thumbnails"][0]["url"].split("?")[0]
        return title, duration_min, thumbnail, vidid

    # --- Cleaned Download Function (API/Cache Removed) ---
    
    async def download(
        self,
        link: str,
        mystic,
        video: Union[bool, str] = None,
        videoid: Union[bool, str] = None,
        songaudio: Union[bool, str] = None,
        songvideo: Union[bool, str] = None,
        format_id: Union[bool, str] = None,
        title: Union[bool, str] = None,
    ) -> tuple[str, bool]:
        if videoid:
            link = self.base + link
        loop = asyncio.get_running_loop()
        cookie_file = get_cookies()

        # --- (Slow Download) Fallback Functions ---
        def audio_dl_fallback():
            """Slow Download (Fallback) for Audio"""
            ydl_optssx = {
                "format": "bestaudio[ext=m4a]/bestaudio/best",
                "outtmpl": "downloads/%(id)s.%(ext)s",
                "geo_bypass": True,
                "nocheckcertificate": True,
                "quiet": True,
                "no_warnings": True,
            }
            if cookie_file:
                ydl_optssx["cookiefile"] = cookie_file
            x = yt_dlp.YoutubeDL(ydl_optssx)
            info = x.extract_info(link, False)
            xyz = os.path.join("downloads", f"{info['id']}.{info['ext']}")
            if not os.path.exists(xyz):
                x.download([link])
            return xyz

        def video_dl_fallback():
            """Slow Download (Fallback) for Video"""
            ydl_optssx = {
                "format": "bestvideo[height<=?720][width<=?1280]+bestaudio/best[height<=?720][width<=?1280]",
                "outtmpl": "downloads/%(id)s.%(ext)s",
                "geo_bypass": True,
                "nocheckcertificate": True,
                "quiet": True,
                "no_warnings": True,
                "prefer_ffmpeg": True,
                "merge_output_format": "mp4",
            }
            if cookie_file:
                ydl_optssx["cookiefile"] = cookie_file
            x = yt_dlp.YoutubeDL(ydl_optssx)
            info = x.extract_info(link, False)
            xyz = os.path.join("downloads", f"{info['id']}.mp4")
            if not os.path.exists(xyz):
                x.download([link])
            return xyz
        
        # --- Direct Downloads (/song command) ---
        if songvideo:
            def song_video_dl():
                formats = f"{format_id}+140"
                fpath = f"downloads/{title}"
                ydl_optssx = {"format": formats, "outtmpl": fpath, "geo_bypass": True, "nocheckcertificate": True, "quiet": True, "no_warnings": True, "prefer_ffmpeg": True, "merge_output_format": "mp4"}
                if cookie_file: ydl_optssx["cookiefile"] = cookie_file
                x = yt_dlp.YoutubeDL(ydl_optssx); x.download([link])
            await loop.run_in_executor(None, song_video_dl)
            fpath = f"downloads/{title}.mp4"
            return fpath, True 
            
        elif songaudio:
            def song_audio_dl():
                fpath = f"downloads/{title}.%(ext)s"
                ydl_optssx = {"format": format_id, "outtmpl": fpath, "geo_bypass": True, "nocheckcertificate": True, "quiet": True, "no_warnings": True, "prefer_ffmpeg": True, "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "320"}]}
                if cookie_file: ydl_optssx["cookiefile"] = cookie_file
                x = yt_dlp.YoutubeDL(ydl_optssx); x.download([link])
            await loop.run_in_executor(None, song_audio_dl)
            fpath = f"downloads/{title}.mp3"
            return fpath, True

        # --- Fast Join Logic (Pure yt-dlp stream) ---
        else:
            if video:
                logger.info(f"Fast Join (Video) requested for: {link}")
                format = "bestvideo[height<=?720][width<=?1280]+bestaudio/best[height<=?720][width<=?1280]"
                fallback_func = video_dl_fallback
            else:
                logger.info(f"Fast Join (Audio) requested for: {link}")
                format = "bestaudio[ext=m4a]/bestaudio/best"
                fallback_func = audio_dl_fallback

            proc_args = ["yt-dlp", "-g", "-f", format]
            if cookie_file:
                proc_args.extend(["--cookies", cookie_file])
            proc_args.append(link)

            proc = await asyncio.create_subprocess_exec(
                *proc_args,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await proc.communicate()
            
            if stdout:
                stream_link = stdout.decode().split("\n")[0]
                logger.info(f"Fast Join (Stream Link) found: {stream_link[:50]}...")
                return stream_link, False  # Return (URL, direct=False)
            else:
                logger.warning(f"FAST STREAM မရပါ ({'Video' if video else 'Audio'})။ SLOW DOWNLOAD သို့ Fallback လုပ်နေပါသည်: {stderr.decode()}")
                downloaded_file = await loop.run_in_executor(None, fallback_func)
                return downloaded_file, True # Return (Local File Path, direct=True)
