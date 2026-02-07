import asyncio
import os
import re
import json
from typing import Union, Dict, List
import yt_dlp
from pyrogram.enums import MessageEntityType
from pyrogram.types import Message
from youtubesearchpython.__future__ import VideosSearch
from maythusharmusic.utils.formatters import time_to_seconds
import aiohttp
from maythusharmusic import LOGGER
import hashlib
import time

class RenderProAPI:
    """Professional API client for Render Pro hosted service"""
    
    def __init__(self):
        # Render Pro API endpoint
        self.api_url = "https://maythushar-youtube-api.onrender.com"
        
        # Fallback APIs (if Render is down)
        self.fallback_apis = [
            "https://youtube-api-pro-1.onrender.com",
            "https://youtube-api-pro-2.onrender.com",
            "https://music-api-pro.onrender.com"
        ]
        
        # Cache for video info
        self.info_cache = {}
        self.cache_timeout = 300  # 5 minutes
        
        # Session for HTTP requests
        self.session = None
        
    async def get_session(self):
        """Get or create aiohttp session"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30),
                headers={
                    'User-Agent': 'MayThuSharMusicBot/2.0',
                    'Accept': 'application/json'
                }
            )
        return self.session
        
    async def close_session(self):
        """Close the HTTP session"""
        if self.session and not self.session.closed:
            await self.session.close()
            
    def extract_video_id(self, url: str) -> str:
        """Extract YouTube video ID from URL"""
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([a-zA-Z0-9_-]{11})',
            r'^([a-zA-Z0-9_-]{11})$'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match[1]
        
        return None
        
    async def get_api_status(self, api_url: str = None) -> bool:
        """Check if API is online"""
        url = api_url or self.api_url
        session = await self.get_session()
        
        try:
            async with session.get(f"{url}/health", timeout=5) as response:
                return response.status == 200
        except:
            return False
            
    async def get_active_api(self) -> str:
        """Get first working API endpoint"""
        # Try main API first
        if await self.get_api_status(self.api_url):
            return self.api_url
            
        # Try fallbacks
        for api in self.fallback_apis:
            if await self.get_api_status(api):
                return api
                
        # Try to create a new Render instance
        new_api = await self.deploy_backup_api()
        if new_api:
            return new_api
            
        return None
        
    async def deploy_backup_api(self) -> str:
        """Deploy backup API on Render (requires Render API key)"""
        # This would use Render API to deploy a new instance
        # For now, return None
        return None
        
    async def get_video_info(self, url: str) -> Dict:
        """Get video information from API"""
        video_id = self.extract_video_id(url)
        if not video_id:
            return None
            
        # Check cache
        cache_key = f"info_{video_id}"
        if cache_key in self.info_cache:
            cached_data, timestamp = self.info_cache[cache_key]
            if time.time() - timestamp < self.cache_timeout:
                return cached_data
                
        api_url = await self.get_active_api()
        if not api_url:
            return None
            
        session = await self.get_session()
        
        try:
            async with session.get(
                f"{api_url}/api/info",
                params={"url": url},
                timeout=10
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success"):
                        # Cache the result
                        self.info_cache[cache_key] = (data, time.time())
                        return data
                        
        except Exception as e:
            LOGGER.error(f"Error getting video info: {e}")
            
        return None
        
    async def download_audio(self, url: str, quality: str = "high") -> str:
        """Download audio using Render Pro API"""
        video_id = self.extract_video_id(url)
        if not video_id:
            return None
            
        # Download directory
        DOWNLOAD_DIR = "downloads"
        os.makedirs(DOWNLOAD_DIR, exist_ok=True)
        
        # Check if file already exists
        file_path = os.path.join(DOWNLOAD_DIR, f"{video_id}_{quality}.mp3")
        if os.path.exists(file_path):
            return file_path
            
        api_url = await self.get_active_api()
        if not api_url:
            return await self.direct_download(url)
            
        session = await self.get_session()
        
        try:
            # Get download URL
            download_url = f"{api_url}/api/audio?url={url}&quality={quality}&bitrate=192"
            
            async with session.get(download_url, timeout=120) as response:
                if response.status == 200:
                    with open(file_path, "wb") as f:
                        async for chunk in response.content.iter_chunked(8192):
                            f.write(chunk)
                            
                    LOGGER.info(f"Downloaded audio: {file_path}")
                    return file_path
                    
        except Exception as e:
            LOGGER.error(f"API download failed: {e}")
            
        # Fallback to direct download
        return await self.direct_download(url)
        
    async def download_studio_audio(self, url: str) -> str:
        """Download studio quality audio"""
        video_id = self.extract_video_id(url)
        if not video_id:
            return None
            
        DOWNLOAD_DIR = "downloads"
        os.makedirs(DOWNLOAD_DIR, exist_ok=True)
        
        file_path = os.path.join(DOWNLOAD_DIR, f"{video_id}_studio.mp3")
        if os.path.exists(file_path):
            return file_path
            
        api_url = await self.get_active_api()
        if not api_url:
            return await self.enhance_audio_locally(url)
            
        session = await self.get_session()
        
        try:
            download_url = f"{api_url}/api/studio?url={url}"
            
            async with session.get(download_url, timeout=180) as response:
                if response.status == 200:
                    with open(file_path, "wb") as f:
                        async for chunk in response.content.iter_chunked(8192):
                            f.write(chunk)
                            
                    return file_path
                    
        except Exception as e:
            LOGGER.error(f"Studio audio download failed: {e}")
            
        return await self.enhance_audio_locally(url)
        
    async def download_video(self, url: str, quality: str = "360p") -> str:
        """Download video using API"""
        video_id = self.extract_video_id(url)
        if not video_id:
            return None
            
        DOWNLOAD_DIR = "downloads"
        os.makedirs(DOWNLOAD_DIR, exist_ok=True)
        
        file_path = os.path.join(DOWNLOAD_DIR, f"{video_id}_{quality}.mp4")
        if os.path.exists(file_path):
            return file_path
            
        api_url = await self.get_active_api()
        if not api_url:
            return await self.direct_video_download(url, quality)
            
        session = await self.get_session()
        
        try:
            download_url = f"{api_url}/api/video?url={url}&quality={quality}"
            
            async with session.get(download_url, timeout=300) as response:
                if response.status == 200:
                    with open(file_path, "wb") as f:
                        async for chunk in response.content.iter_chunked(8192):
                            f.write(chunk)
                            
                    return file_path
                    
        except Exception as e:
            LOGGER.error(f"Video download failed: {e}")
            
        return await self.direct_video_download(url, quality)
        
    async def direct_download(self, url: str) -> str:
        """Direct download using yt-dlp (fallback)"""
        video_id = self.extract_video_id(url)
        if not video_id:
            return None
            
        DOWNLOAD_DIR = "downloads"
        os.makedirs(DOWNLOAD_DIR, exist_ok=True)
        
        file_path = os.path.join(DOWNLOAD_DIR, f"{video_id}.mp3")
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': file_path.replace('.mp3', '.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': True,
            'no_warnings': True,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
                
            return file_path
            
        except Exception as e:
            LOGGER.error(f"Direct download failed: {e}")
            return None
            
    async def direct_video_download(self, url: str, quality: str) -> str:
        """Direct video download using yt-dlp"""
        video_id = self.extract_video_id(url)
        if not video_id:
            return None
            
        DOWNLOAD_DIR = "downloads"
        os.makedirs(DOWNLOAD_DIR, exist_ok=True)
        
        file_path = os.path.join(DOWNLOAD_DIR, f"{video_id}.mp4")
        
        # Map quality to yt-dlp format
        format_map = {
            '144p': 'worst',
            '240p': 'worst',
            '360p': '18',
            '480p': '135',
            '720p': '22',
            '1080p': '137',
            'highest': 'best'
        }
        
        format_id = format_map.get(quality, '18')
        
        ydl_opts = {
            'format': f'{format_id}+bestaudio/best' if format_id != 'best' else 'best',
            'outtmpl': file_path,
            'merge_output_format': 'mp4',
            'quiet': True,
            'no_warnings': True,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
                
            return file_path
            
        except Exception as e:
            LOGGER.error(f"Direct video download failed: {e}")
            return None
            
    async def enhance_audio_locally(self, url: str) -> str:
        """Local audio enhancement (fallback for studio quality)"""
        video_id = self.extract_video_id(url)
        if not video_id:
            return None
            
        DOWNLOAD_DIR = "downloads"
        os.makedirs(DOWNLOAD_DIR, exist_ok=True)
        
        file_path = os.path.join(DOWNLOAD_DIR, f"{video_id}_studio.mp3")
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(DOWNLOAD_DIR, f"{video_id}.%(ext)s"),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '320',
            }],
            'postprocessor_args': [
                '-ar', '48000',
                '-ac', '2',
                '-b:a', '320k',
                '-af', 'volume=1.5,highpass=f=80,lowpass=f=16000'
            ],
            'quiet': True,
            'no_warnings': True,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
                
            # Find the downloaded file
            for file in os.listdir(DOWNLOAD_DIR):
                if file.startswith(f"{video_id}.") and file.endswith('.mp3'):
                    temp_path = os.path.join(DOWNLOAD_DIR, file)
                    if temp_path != file_path:
                        os.rename(temp_path, file_path)
                    return file_path
                    
        except Exception as e:
            LOGGER.error(f"Local enhancement failed: {e}")
            
        return None
        
    async def get_formats(self, url: str) -> List[Dict]:
        """Get available formats for a video"""
        api_url = await self.get_active_api()
        if not api_url:
            return []
            
        session = await self.get_session()
        
        try:
            async with session.get(
                f"{api_url}/api/formats?url={url}",
                timeout=10
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success"):
                        return data.get("formats", [])
                        
        except Exception as e:
            LOGGER.error(f"Error getting formats: {e}")
            
        return []

# Global API instance
render_api = RenderProAPI()

# Update existing functions to use new API
async def download_song(link: str, quality: str = "high") -> str:
    """Download song using Render Pro API"""
    return await render_api.download_audio(link, quality)
    
async def download_studio_voice(link: str) -> str:
    """Download studio quality audio"""
    return await render_api.download_studio_audio(link)
    
async def download_video(link: str, quality: str = "360p") -> str:
    """Download video using Render Pro API"""
    return await render_api.download_video(link, quality)

# Keep existing YouTubeAPI class but update download method
class YouTubeAPI:
    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.regex = r"(?:youtube\.com|youtu\.be)"
        self.status = "https://www.youtube.com/oembed?url="
        self.listbase = "https://youtube.com/playlist?list="
        self.reg = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
        self.render_api = render_api

    async def exists(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        return bool(re.search(self.regex, link))

    async def url(self, message_1: Message) -> Union[str, None]:
        messages = [message_1]
        if message_1.reply_to_message:
            messages.append(message_1.reply_to_message)
        for message in messages:
            if message.entities:
                for entity in message.entities:
                    if entity.type == MessageEntityType.URL:
                        text = message.text or message.caption
                        return text[entity.offset: entity.offset + entity.length]
            elif message.caption_entities:
                for entity in message.caption_entities:
                    if entity.type == MessageEntityType.TEXT_LINK:
                        return entity.url
        return None

    async def details(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        
        # Try API first for better info
        info = await self.render_api.get_video_info(link)
        if info:
            return (
                info.get("title", "Unknown"),
                info.get("durationFormatted", "0:00"),
                info.get("duration", 0),
                info.get("thumbnail", ""),
                info.get("videoId", "")
            )
        
        # Fallback to old method
        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            title = result["title"]
            duration_min = result["duration"]
            thumbnail = result["thumbnails"][0]["url"].split("?")[0]
            vidid = result["id"]
            duration_sec = int(time_to_seconds(duration_min)) if duration_min else 0
        return title, duration_min, duration_sec, thumbnail, vidid

    async def title(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            return result["title"]

    async def duration(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            return result["duration"]

    async def thumbnail(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            return result["thumbnails"][0]["url"].split("?")[0]

    async def video(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        try:
            downloaded_file = await download_video(link)
            if downloaded_file:
                return 1, downloaded_file
            else:
                return 0, "Video download failed"
        except Exception as e:
            return 0, f"Video download error: {e}"

    async def playlist(self, link, limit, user_id, videoid: Union[bool, str] = None):
        if videoid:
            link = self.listbase + link
        if "&" in link:
            link = link.split("&")[0]
        playlist = await shell_cmd(
            f"yt-dlp -i --get-id --flat-playlist --playlist-end {limit} --skip-download {link}"
        )
        try:
            result = [key for key in playlist.split("\n") if key]
        except:
            result = []
        return result

    async def track(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            title = result["title"]
            duration_min = result["duration"]
            vidid = result["id"]
            yturl = result["link"]
            thumbnail = result["thumbnails"][0]["url"].split("?")[0]
        track_details = {
            "title": title,
            "link": yturl,
            "vidid": vidid,
            "duration_min": duration_min,
            "thumb": thumbnail,
        }
        return track_details, vidid

    async def formats(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        
        # Try API first
        formats = await self.render_api.get_formats(link)
        if formats:
            return formats, link
            
        # Fallback
        ytdl_opts = {"quiet": True}
        ydl = yt_dlp.YoutubeDL(ytdl_opts)
        with ydl:
            formats_available = []
            r = ydl.extract_info(link, download=False)
            for format in r["formats"]:
                try:
                    if "dash" not in str(format["format"]).lower():
                        formats_available.append(
                            {
                                "format": format["format"],
                                "filesize": format.get("filesize"),
                                "format_id": format["format_id"],
                                "ext": format["ext"],
                                "format_note": format["format_note"],
                                "yturl": link,
                            }
                        )
                except:
                    continue
        return formats_available, link

    async def slider(self, link: str, query_type: int, videoid: Union[bool, str] = None):
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
        studio_voice: Union[bool, str] = None,
        crystal_clear: Union[bool, str] = None,
        quality: str = "high"
    ) -> str:
        if videoid:
            link = self.base + link

        try:
            if video:
                downloaded_file = await download_video(link, quality)
            elif crystal_clear or studio_voice:
                downloaded_file = await download_studio_voice(link)
                if not downloaded_file:
                    downloaded_file = await download_song(link, "320")
            else:
                downloaded_file = await download_song(link, quality)
            
            if downloaded_file:
                return downloaded_file, True
            else:
                return None, False
        except Exception as e:
            LOGGER.error(f"Download error: {e}")
            return None, False

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

# Initialize API on startup
async def init_render_api():
    """Initialize Render API on startup"""
    LOGGER.info("Initializing Render Pro API...")
    status = await render_api.get_api_status()
    if status:
        LOGGER.info("Render Pro API is online")
    else:
        LOGGER.warning("Render Pro API is offline, using fallbacks")
    return status

# Auto-initialize
try:
    loop = asyncio.get_event_loop()
    if loop.is_running():
        asyncio.create_task(init_render_api())
    else:
        loop.run_until_complete(init_render_api())
except:
    pass
