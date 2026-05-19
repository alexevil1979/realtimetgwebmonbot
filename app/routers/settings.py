import logging

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.dependencies import login_redirect, optional_user
from app.models import AppSetting, User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/settings", tags=["settings"])
templates = Jinja2Templates(directory="app/templates")


@router.get("", response_class=HTMLResponse)
async def settings_page(request: Request, user: User | None = Depends(optional_user)):
    if not user:
        return login_redirect()

    settings = await AppSetting.get_all()
    return templates.TemplateResponse(
        request,
        "settings.html",
        {"request": request, "user": user, "settings": settings, "saved": False},
    )


@router.post("")
async def settings_save(
    request: Request,
    user: User | None = Depends(optional_user),
    telegram_bot_token: str = Form(""),
    telegram_chat_id: str = Form(""),
    notify_on_up: str | None = Form(None),
    notify_cooldown_minutes: int = Form(15),
):
    if not user:
        return login_redirect()

    await AppSetting.set("telegram_bot_token", telegram_bot_token.strip())
    await AppSetting.set("telegram_chat_id", telegram_chat_id.strip())
    await AppSetting.set("notify_on_up", "true" if notify_on_up == "on" else "false")
    await AppSetting.set(
        "notify_cooldown_minutes",
        str(max(1, min(notify_cooldown_minutes, 1440))),
    )

    logger.info("Settings updated by %s", user.username)
    settings = await AppSetting.get_all()
    return templates.TemplateResponse(
        request,
        "settings.html",
        {"request": request, "user": user, "settings": settings, "saved": True},
    )
