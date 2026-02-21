# stream.py
import os
from random import randint
from typing import Union

from pyrogram.types import InlineKeyboardMarkup

import config
from maythusharmusic import Carbon, YouTube, app
from maythusharmusic.core.call import Hotty
from maythusharmusic.misc import db
from maythusharmusic.utils.database import add_active_video_chat, is_active_chat
from maythusharmusic.utils.exceptions import AssistantErr
from maythusharmusic.utils.inline import aq_markup, close_markup, stream_markup
from maythusharmusic.utils.pastebin import HottyBin
from maythusharmusic.utils.stream.queue import put_queue, put_queue_index
from maythusharmusic.utils.thumbnails import get_thumb


async def stream(
    _,
    mystic,
    user_id,
    result,
    chat_id,
    user_name,
    original_chat_id,
    video: Union[bool, str] = None,
    streamtype: Union[bool, str] = None,
    spotify: Union[bool, str] = None,
    forceplay: Union[bool, str] = None,
):
    if not result:
        return

    if forceplay:
        await Hotty.force_stop_stream(chat_id)

    # ------------------------------------------------------------------
    # PLAYLIST
    # ------------------------------------------------------------------
    if streamtype == "playlist":
        msg = f"{_['play_19']}\n\n"
        count = 0

        for search in result:
            if int(count) == config.PLAYLIST_FETCH_LIMIT:
                continue

            try:
                (
                    title,
                    duration_min,
                    duration_sec,
                    thumbnail,
                    vidid,
                ) = await YouTube.details(search, False if spotify else True)
            except Exception:
                continue

            if str(duration_min) == "None":
                continue

            if duration_sec > config.DURATION_LIMIT:
                continue

            if await is_active_chat(chat_id):
                await put_queue(
                    chat_id,
                    original_chat_id,
                    f"vid_{vidid}",
                    title,
                    duration_min,
                    user_name,
                    vidid,
                    user_id,
                    "video" if video else "audio",
                )

                position = len(db.get(chat_id)) - 1
                count += 1
                msg += f"{count}. {title[:70]}\n"
                msg += f"{_['play_20']} {position}\n\n"

            else:
                if not forceplay:
                    db[chat_id] = []

                status = True if video else None

                # 🔥 TAMAMEN TÜRKÇE İNDİRME MESAJI
                try:
                    await mystic.edit_text(_["play_dl"].format(title))
                except Exception:
                    await mystic.edit_text(f"İndiriliyor ● ᥫ᭡ {title}")

                try:
                    file_path, direct = await YouTube.download(
                        vidid, mystic, video=status, videoid=True
                    )
                except Exception:
                    raise AssistantErr(_["play_14"])

                await Hotty.join_call(
                    chat_id,
                    original_chat_id,
                    file_path,
                    video=status,
                    image=thumbnail,
                )

                await put_queue(
                    chat_id,
                    original_chat_id,
                    file_path if direct else f"vid_{vidid}",
                    title,
                    duration_min,
                    user_name,
                    vidid,
                    user_id,
                    "video" if video else "audio",
                    forceplay=forceplay,
                )

                img = await get_thumb(vidid)
                button = stream_markup(_, chat_id)

                run = await app.send_photo(
                    original_chat_id,
                    photo=img,
                    caption=_["stream_1"].format(
                        f"https://t.me/{app.username}?start=info_{vidid}",
                        title[:23],
                        duration_min,
                        user_name,
                    ),
                    reply_markup=InlineKeyboardMarkup(button),
                )

                db[chat_id][0]["mystic"] = run
                db[chat_id][0]["markup"] = "stream"

        if count == 0:
            return

        link = await HottyBin(msg)
        lines = msg.count("\n")
        car = msg if lines < 17 else os.linesep.join(msg.split(os.linesep)[:17])
        carbon = await Carbon.generate(car, randint(100, 10000000))
        upl = close_markup(_)

        return await app.send_photo(
            original_chat_id,
            photo=carbon,
            caption=_["play_21"].format(position, link),
            reply_markup=upl,
        )

    # ------------------------------------------------------------------
    # YOUTUBE
    # ------------------------------------------------------------------
    elif streamtype == "youtube":

        link = result["link"]
        vidid = result["vidid"]
        title = result["title"].title()
        duration_min = result["duration_min"]
        thumbnail = result["thumb"]
        status = True if video else None

        if db.get(chat_id) and len(db.get(chat_id)) >= 50:
            return await app.send_message(
                original_chat_id,
                "Kuyruğa en fazla 50 parça ekleyebilirsin."
            )

        # 🔥 TÜRKÇE İNDİRME MESAJI
        try:
            await mystic.edit_text(_["play_dl"].format(title))
        except Exception:
            await mystic.edit_text(f"İndiriliyor ● ᥫ᭡ {title}")

        try:
            file_path, direct = await YouTube.download(
                vidid, mystic, videoid=True, video=status
            )
        except Exception:
            raise AssistantErr(_["play_14"])

        if await is_active_chat(chat_id):

            await put_queue(
                chat_id,
                original_chat_id,
                file_path,
                title,
                duration_min,
                user_name,
                vidid,
                user_id,
                "video" if video else "audio",
            )

            position = len(db.get(chat_id)) - 1
            button = aq_markup(_, chat_id)

            await app.send_message(
                original_chat_id,
                text=_["queue_4"].format(position, title[:27], duration_min, user_name),
                reply_markup=InlineKeyboardMarkup(button),
            )

        else:

            db[chat_id] = []
            await Hotty.join_call(
                chat_id,
                original_chat_id,
                file_path,
                video=status,
                image=thumbnail,
            )

            await put_queue(
                chat_id,
                original_chat_id,
                file_path,
                title,
                duration_min,
                user_name,
                vidid,
                user_id,
                "video" if video else "audio",
                forceplay=forceplay,
            )

            img = await get_thumb(vidid)
            button = stream_markup(_, chat_id)

            run = await app.send_photo(
                original_chat_id,
                photo=img,
                caption=_["stream_1"].format(
                    f"https://t.me/{app.username}?start=info_{vidid}",
                    title[:23],
                    duration_min,
                    user_name,
                ),
                reply_markup=InlineKeyboardMarkup(button),
            )

            db[chat_id][0]["mystic"] = run
            db[chat_id][0]["markup"] = "stream"
