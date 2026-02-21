import math
from pyrogram.types import InlineKeyboardButton
from maythusharmusic.utils.formatters import time_to_seconds


# ---------------- PURE FIRE TIMER ----------------

def _fire_line(played_sec: int, duration_sec: int, width: int = 18) -> str:
    """
    PURE FIRE TIMER alt satırı.
    width: alt çizgi uzunluğu (buton text'i için ideal: 16-22 arası)
    """
    width = max(14, min(24, width))

    if duration_sec <= 0:
        ratio = 0.0
    else:
        ratio = max(0.0, min(1.0, played_sec / duration_sec))

    percent = int(ratio * 100)
    pos = int(round(ratio * (width - 1)))

    left = pos
    right = (width - 1) - pos

    # 0-29%: kıvılcım hafif
    if percent < 30:
        # küçük kıvılcım noktası
        return f"{'·'*max(0,left-1)}✨{'·'* (right)}"

    # 30-64%: tek alev + çizgi
    if percent < 65:
        return f"{'═'*left}🔥{'═'*right}"

    # 65-94%: yoğun alev + kıvılcım uçları
    if percent < 95:
        # alev bloğunu merkezde daha güçlü göster
        core = "🔥🔥🔥"
        # uzunluğu taşırmamak için core'u sabitleyip geri kalanını çizgilerle doldur
        # pos'a göre core'u kaydır
        pad_left = max(0, left - 2)
        pad_right = max(0, right - 2)
        line = f"{'═'*pad_left}⚡{core}⚡{'═'*pad_right}"
        # garanti uzunluk
        return line[:width]

    # 95-100%: overload final
    return "💥🔥🔥🔥🔥🔥🔥💥"


def _pure_fire_timer_buttons(played: str, dur: str):
    ps = time_to_seconds(played)
    ds = time_to_seconds(dur)

    if ds > 0:
        ps = min(max(0, ps), ds)
    else:
        ps = max(0, ps)

    top = f"⟦ {played}  ⟡  {dur} ⟧"
    bottom = _fire_line(ps, ds, width=18)

    return [
        [InlineKeyboardButton(top, callback_data="GetTimer")],
        [InlineKeyboardButton(bottom, callback_data="GetTimer")],
    ]


# ---------------- SENİN MARKUP'LAR ----------------

def track_markup(_, videoid, user_id, channel, fplay):
    return [
        [
            InlineKeyboardButton(text=_["P_B_1"], callback_data=f"MusicStream {videoid}|{user_id}|a|{channel}|{fplay}"),
            InlineKeyboardButton(text=_["P_B_2"], callback_data=f"MusicStream {videoid}|{user_id}|v|{channel}|{fplay}"),
        ],
        [
            InlineKeyboardButton(text=_["CLOSE_BUTTON"], callback_data=f"forceclose {videoid}|{user_id}"),
        ],
    ]


def stream_markup_timer(_, chat_id, played, dur):
    buttons = [
        [
            InlineKeyboardButton(text="⟪ PLAY ⟫", callback_data=f"ADMIN Resume|{chat_id}"),
            InlineKeyboardButton(text="⟪ PAUSE ⟫", callback_data=f"ADMIN Pause|{chat_id}"),
            InlineKeyboardButton(text="⟪ STOP ⟫", callback_data=f"ADMIN Stop|{chat_id}"),
            InlineKeyboardButton(text="⟪ RESET ⟫", callback_data=f"ADMIN Replay|{chat_id}"),
        ],
        [
            InlineKeyboardButton(text="⟪ BACK ⟫", callback_data=f"ADMIN Previous|{chat_id}"),
            InlineKeyboardButton(text="⟪ NEXT ⟫", callback_data=f"ADMIN Skip|{chat_id}"),
        ],
    ]

    # PURE FIRE TIMER satırları (2 satır ekler)
    buttons.extend(_pure_fire_timer_buttons(played, dur))

    # Linkler (senin sabitlerin)
    buttons.extend([
        [
            InlineKeyboardButton(text="Owner", url="https://t.me/kral_surucu"),
            InlineKeyboardButton(text="Support", url="https://t.me/MUHABBET_SOFASI_TR"),
        ],
        [InlineKeyboardButton(text="KURUCU", url="https://t.me/kral_surucu")],
    ])
    return buttons


def stream_markup(_, chat_id):
    return [
        [
            InlineKeyboardButton(text="⟪ PLAY ⟫", callback_data=f"ADMIN Resume|{chat_id}"),
            InlineKeyboardButton(text="⟪ PAUSE ⟫", callback_data=f"ADMIN Pause|{chat_id}"),
            InlineKeyboardButton(text="⟪ STOP ⟫", callback_data=f"ADMIN Stop|{chat_id}"),
            InlineKeyboardButton(text="⟪ RESET ⟫", callback_data=f"ADMIN Replay|{chat_id}"),
        ],
        [
            InlineKeyboardButton(text="⟪ BACK ⟫", callback_data=f"ADMIN Previous|{chat_id}"),
            InlineKeyboardButton(text="⟪ NEXT ⟫", callback_data=f"ADMIN Skip|{chat_id}"),
        ],
        [
            InlineKeyboardButton(text="Owner", url="https://t.me/kral_surucu"),
            InlineKeyboardButton(text="Support", url="https://t.me/MUHABBET_SOFASI_TR"),
        ],
        [InlineKeyboardButton(text="KURUCU", url="https://t.me/kral_surucu")],
    ]


def playlist_markup(_, videoid, user_id, ptype, channel, fplay):
    return [
        [
            InlineKeyboardButton(
                text=_["P_B_1"],
                callback_data=f"AnonyPlaylists {videoid}|{user_id}|{ptype}|a|{channel}|{fplay}",
            ),
            InlineKeyboardButton(
                text=_["P_B_2"],
                callback_data=f"AnonyPlaylists {videoid}|{user_id}|{ptype}|v|{channel}|{fplay}",
            ),
        ],
        [
            InlineKeyboardButton(text=_["CLOSE_BUTTON"], callback_data=f"forceclose {videoid}|{user_id}"),
        ],
    ]


def livestream_markup(_, videoid, user_id, mode, channel, fplay):
    return [
        [
            InlineKeyboardButton(
                text=_["P_B_3"],
                callback_data=f"LiveStream {videoid}|{user_id}|{mode}|{channel}|{fplay}",
            ),
        ],
        [
            InlineKeyboardButton(text=_["CLOSE_BUTTON"], callback_data=f"forceclose {videoid}|{user_id}"),
        ],
    ]


def slider_markup(_, videoid, user_id, query, query_type, channel, fplay):
    query = f"{query[:20]}"
    return [
        [
            InlineKeyboardButton(text=_["P_B_1"], callback_data=f"MusicStream {videoid}|{user_id}|a|{channel}|{fplay}"),
            InlineKeyboardButton(text=_["P_B_2"], callback_data=f"MusicStream {videoid}|{user_id}|v|{channel}|{fplay}"),
        ],
        [
            InlineKeyboardButton(text="◁", callback_data=f"slider B|{query_type}|{query}|{user_id}|{channel}|{fplay}"),
            InlineKeyboardButton(text=_["CLOSE_BUTTON"], callback_data=f"forceclose {query}|{user_id}"),
            InlineKeyboardButton(text="▷", callback_data=f"slider F|{query_type}|{query}|{user_id}|{channel}|{fplay}"),
        ],
                                 ]
