from urllib.parse import urlparse

from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse

from app.config import SESSION_MAX_AGE
from app.i18n import LANG_COOKIE, normalize_lang
from app.models import AppSetting

router = APIRouter(tags=["i18n"])


def _safe_next(url: str) -> str:
    if not url or not url.startswith("/") or url.startswith("//"):
        return "/"
    parsed = urlparse(url)
    if parsed.netloc:
        return "/"
    return url


@router.get("/lang/{code}")
async def set_language(request: Request, code: str, next: str = "/"):
    lang = normalize_lang(code)
    target = _safe_next(next)
    response = RedirectResponse(target, status_code=303)
    response.set_cookie(
        LANG_COOKIE,
        lang,
        httponly=False,
        samesite="lax",
        max_age=SESSION_MAX_AGE,
    )
    await AppSetting.set("ui_language", lang)
    return response
