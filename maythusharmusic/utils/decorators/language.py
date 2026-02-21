from strings import get_string
from maythusharmusic.misc import SUDOERS
from maythusharmusic.utils.database import get_lang, is_maintenance

# Bu dosyada app / SUPPORT_CHAT tanımlı değilse patlamasın diye güvenli kullanım:
try:
    from maythusharmusic import app
except Exception:
    app = None

try:
    from config import SUPPORT_CHAT
except Exception:
    SUPPORT_CHAT = None


def _fallback_language():
    # Hata olursa TR'ye düş
    try:
        return get_string("tr")
    except Exception:
        # Eğer "tr" dosyası yoksa en azından english'e düşsün
        return get_string("en")


def language(mystic):
    async def wrapper(_, message, **kwargs):
        # Maintenance kontrolü (senin mantığın: is_maintenance False ise bakım var)
        if await is_maintenance() is False:
            if message.from_user and message.from_user.id not in SUDOERS:
                mention = getattr(app, "mention", "Bot") if app else "Bot"
                if SUPPORT_CHAT:
                    txt = (
                        f"{mention} bakımda. Sebebi öğrenmek için "
                        f"<a href={SUPPORT_CHAT}>destek sohbetine</a> gel."
                    )
                else:
                    txt = f"{mention} bakımda."
                return await message.reply_text(
                    text=txt,
                    disable_web_page_preview=True,
                )

        try:
            await message.delete()
        except Exception:
            pass

        try:
            lang_code = await get_lang(message.chat.id)
            language_obj = get_string(lang_code)
        except Exception:
            language_obj = _fallback_language()

        return await mystic(_, message, language_obj)

    return wrapper


def languageCB(mystic):
    async def wrapper(_, CallbackQuery, **kwargs):
        if await is_maintenance() is False:
            if CallbackQuery.from_user and CallbackQuery.from_user.id not in SUDOERS:
                mention = getattr(app, "mention", "Bot") if app else "Bot"
                return await CallbackQuery.answer(
                    f"{mention} bakımda. Sebebi için destek sohbetine gel.",
                    show_alert=True,
                )

        try:
            lang_code = await get_lang(CallbackQuery.message.chat.id)
            language_obj = get_string(lang_code)
        except Exception:
            language_obj = _fallback_language()

        return await mystic(_, CallbackQuery, language_obj)

    return wrapper


def LanguageStart(mystic):
    async def wrapper(_, message, **kwargs):
        try:
            lang_code = await get_lang(message.chat.id)
            language_obj = get_string(lang_code)
        except Exception:
            language_obj = _fallback_language()

        return await mystic(_, message, language_obj)

    return wrapper
