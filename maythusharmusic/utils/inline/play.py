import re
from pyrogram.types import InlineKeyboardButton
from maythusharmusic.utils.formatters import time_to_seconds


# ---------- KIRMIZI YER (GÖRÜNMEYEN UNICODE) FIX ----------
def clean_text(text: str) -> str:
    if text is None:
        return ""
    text = str(text)

    # RTL/LTR & direction override karakterleri
    text = re.sub(r'[\u200E\u200F\u202A-\u202E\u2066-\u2069]', '', text)
    # kontrol karakterleri
    text = re.sub(r'[\x00-\x1F\x7F]', '', text)

    return text.strip()


# ---------------- PURE FIRE TIMER ----------------
def _fire_line(played_sec: int, duration_sec: int, width: int = 18) -> str:
    width = max(14, min(24, width))

    if duration_sec <= 0:
        ratio = 0.0
    else:
        ratio = max(0.0, min(1.0, played_sec / duration_sec))

    percent = int(ratio * 100)
    pos = int(round(ratio * (width - 1)))

    left = pos
    right = (width - 1) - pos

    if percent < 30:
        return f"{'·' * max(0, left - 1)}✨{'·' * right}"

    if percent < 65:
        return f"{'═' * left}🔥{'═' * right}"

    if percent < 95:
        core = "🔥🔥🔥"
        pad_left = max(0, left - 2)
        pad_right = max(0, right - 2)
        line = f"{'═' * pad_left}⚡{core}⚡{'═' * pad_right}"
        return line[:width]

    return "💥🔥🔥🔥🔥🔥🔥💥"


def _pure_fire_timer_buttons(played: str, dur: str):
    ps = time_to_seconds(played)
    ds = time_to_seconds(dur)

    if ds > 0:
        ps = min(max(0, ps), ds)
    else:
        ps = max(0, ps)

    top = clean_text(f"⟦ {played}  ⟡  {dur} ⟧")
    bottom = clean_text(_fire_line(ps, ds, width=18))

    return [
        [InlineKeyboardButton(top, callback_data="GetTimer")],
        [InlineKeyboardButton(bottom, callback_data="GetTimer")],
    ]


# ---------------- MARKUP'LAR ----------------
def track_markup(_, videoid, user_id, channel, fplay):
    return [
        [
            InlineKeyboardButton(
                text=clean_text(_["P_B_1"]),
                callback_data=f"MusicStream {videoid}|{user_id}|a|{channel}|{fplay}",
            ),
            InlineKeyboardButton(
                text=clean_text(_["P_B_2"]),
                callback_data=f"MusicStream {videoid}|{user_id}|v|{channel}|{fplay}",
            ),
        ],
        [
            InlineKeyboardButton(
                text=clean_text(_["CLOSE_BUTTON"]),
                callback_data=f"forceclose {videoid}|{user_id}",
            ),
        ],
    ]


def stream_markup_timer(_, chat_id, played, dur):
    buttons = [
        [
            InlineKeyboardButton(text=clean_text("⟪ PLAY ⟫"), callback_data=f"ADMIN Resume|{chat_id}"),
            InlineKeyboardButton(text=clean_text("⟪ PAUSE ⟫"), callback_data=f"ADMIN Pause|{chat_id}"),
            InlineKeyboardButton(text=clean_text("⟪ STOP ⟫"), callback_data=f"ADMIN Stop|{chat_id}"),
            InlineKeyboardButton(text=clean_text("⟪ RESET ⟫"), callback_data=f"ADMIN Replay|{chat_id}"),
        ],
        [
            InlineKeyboardButton(text=clean_text("⟪ BACK ⟫"), callback_data=f"ADMIN Previous|{chat_id}"),
            InlineKeyboardButton(text=clean_text("⟪ NEXT ⟫"), callback_data=f"ADMIN Skip|{chat_id}"),
        ],
    ]

    # PURE FIRE TIMER (2 satır)
    buttons.extend(_pure_fire_timer_buttons(played, dur))

    # Linkler
    buttons.extend([
        [
            InlineKeyboardButton(text=clean_text("Owner"), url="https://t.me/kral_surucu"),
            InlineKeyboardButton(text=clean_text("Support"), url="https://t.me/MUHABBET_SOFASI_TR"),
        ],
        [InlineKeyboardButton(text=clean_text("KURUCU"), url="https://t.me/kral_surucu")],
    ])
    return buttons


def stream_markup(_, chat_id):
    return [
        [
            InlineKeyboardButton(text=clean_text("⟪ PLAY ⟫"), callback_data=f"ADMIN Resume|{chat_id}"),
            InlineKeyboardButton(text=clean_text("⟪ PAUSE ⟫"), callback_data=f"ADMIN Pause|{chat_id}"),
            InlineKeyboardButton(text=clean_text("⟪ STOP ⟫"), callback_data=f"ADMIN Stop|{chat_id}"),
            InlineKeyboardButton(text=clean_text("⟪ RESET ⟫"), callback_data=f"ADMIN Replay|{chat_id}"),
        ],
        [
            InlineKeyboardButton(text=clean_text("⟪ BACK ⟫"), callback_data=f"ADMIN Previous|{chat_id}"),
            InlineKeyboardButton(text=clean_text("⟪ NEXT ⟫"), callback_data=f"ADMIN Skip|{chat_id}"),
        ],
        [
            InlineKeyboardButton(text=clean_text("Owner"), url="https://t.me/kral_surucu"),
            InlineKeyboardButton(text=clean_text("Support"), url="https://t.me/MUHABBET_SOFASI_TR"),
        ],
        [InlineKeyboardButton(text=clean_text("KURUCU"), url="https://t.me/kral_surucu")],
    ]


def playlist_markup(_, videoid, user_id, ptype, channel, fplay):
    return [
        [
            InlineKeyboardButton(
                text=clean_text(_["P_B_1"]),
                callback_data=f"AnonyPlaylists {videoid}|{user_id}|{ptype}|a|{channel}|{fplay}",
            ),
            InlineKeyboardButton(
                text=clean_text(_["P_B_2"]),
                callback_data=f"AnonyPlaylists {videoid}|{user_id}|{ptype}|v|{channel}|{fplay}",
            ),
        ],
        [
            InlineKeyboardButton(
                text=clean_text(_["CLOSE_BUTTON"]),
                callback_data=f"forceclose {videoid}|{user_id}",
            ),
        ],
    ]


def livestream_markup(_, videoid, user_id, mode, channel, fplay):
    return [
        [
            InlineKeyboardButton(
                text=clean_text(_["P_B_3"]),
                callback_data=f"LiveStream {videoid}|{user_id}|{mode}|{channel}|{fplay}",
            ),
        ],
        [
            InlineKeyboardButton(
                text=clean_text(_["CLOSE_BUTTON"]),
                callback_data=f"forceclose {videoid}|{user_id}",
            ),
        ],
    ]


def slider_markup(_, videoid, user_id, query, query_type, channel, fplay):
    query = f"{query[:20]}"
    return [
        [
            InlineKeyboardButton(
                text=clean_text(_["P_B_1"]),
                callback_data=f"MusicStream {videoid}|{user_id}|a|{channel}|{fplay}",
            ),
            InlineKeyboardButton(
                text=clean_text(_["P_B_2"]),
                callback_data=f"MusicStream {videoid}|{user_id}|v|{channel}|{fplay}",
            ),
        ],
        [
            InlineKeyboardButton(
                text=clean_text("◁"),
                callback_data=f"slider B|{query_type}|{query}|{user_id}|{channel}|{fplay}",
            ),
            InlineKeyboardButton(
                text=clean_text(_["CLOSE_BUTTON"]),
                callback_data=f"forceclose {query}|{user_id}",
            ),
            InlineKeyboardButton(
                text=clean_text("▷"),
                callback_data=f"slider F|{query_type}|{query}|{user_id}|{channel}|{fplay}",
            ),
        ],
    ]
