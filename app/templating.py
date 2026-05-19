from fastapi import Request
from fastapi.templating import Jinja2Templates

from app.i18n import SUPPORTED_LANGS, get_locale, translator_for

templates = Jinja2Templates(directory="app/templates")

COFFEE_URL = "https://buymeacoffee.com/alexevil1979"


def template_context(request: Request, **extra) -> dict:
    lang = get_locale(request)
    return {
        "request": request,
        "lang": lang,
        "t": translator_for(lang),
        "supported_langs": SUPPORTED_LANGS,
        "coffee_url": COFFEE_URL,
        **extra,
    }
