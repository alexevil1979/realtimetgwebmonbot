from __future__ import annotations

from fastapi import Request

from app.config import DEFAULT_LANG
from app.i18n.locales import MESSAGES

LANG_COOKIE = "uptime_lang"
SUPPORTED_LANGS = ("ru", "en")


def normalize_lang(code: str | None) -> str:
    if code and code.lower() in SUPPORTED_LANGS:
        return code.lower()
    return DEFAULT_LANG if DEFAULT_LANG in SUPPORTED_LANGS else "ru"


def get_locale(request: Request) -> str:
    cookie = request.cookies.get(LANG_COOKIE)
    if cookie:
        return normalize_lang(cookie)
    accept = request.headers.get("accept-language", "")
    if accept.lower().startswith("en"):
        return "en"
    return normalize_lang(None)


def translate(key: str, lang: str, **kwargs) -> str:
    lang = normalize_lang(lang)
    pack = MESSAGES.get(lang, MESSAGES["ru"])
    text = pack.get(key) or MESSAGES["ru"].get(key) or key
    if kwargs:
        try:
            return text.format(**kwargs)
        except KeyError:
            return text
    return text


def translator_for(lang: str):
    lang = normalize_lang(lang)

    def t(key: str, **kwargs) -> str:
        return translate(key, lang, **kwargs)

    return t
