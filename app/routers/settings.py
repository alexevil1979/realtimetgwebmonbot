import logging

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse

from app.dependencies import login_redirect, optional_user
from app.i18n import get_locale, translate
from app.models import AppSetting, User
from app.services.telegram import send_telegram_raw
from app.templating import template_context, templates

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("", response_class=HTMLResponse)
async def settings_page(request: Request, user: User | None = Depends(optional_user)):
    if not user:
        return login_redirect()

    settings = await AppSetting.get_all()
    return templates.TemplateResponse(
        request,
        "settings.html",
        template_context(
            request,
            user=user,
            settings=settings,
            saved=False,
            test_ok=None,
            test_error=None,
        ),
    )


@router.post("")
async def settings_save(
    request: Request,
    user: User | None = Depends(optional_user),
    telegram_bot_token: str = Form(""),
    telegram_chat_id: str = Form(""),
    notify_on_up: str | None = Form(None),
    notify_down_after_minutes: int = Form(15),
    notify_cooldown_minutes: int = Form(15),
):
    if not user:
        return login_redirect()

    await AppSetting.set("telegram_bot_token", telegram_bot_token.strip())
    await AppSetting.set("telegram_chat_id", telegram_chat_id.strip())
    await AppSetting.set("notify_on_up", "true" if notify_on_up == "on" else "false")
    await AppSetting.set(
        "notify_down_after_minutes",
        str(max(1, min(notify_down_after_minutes, 1440))),
    )
    await AppSetting.set(
        "notify_cooldown_minutes",
        str(max(1, min(notify_cooldown_minutes, 1440))),
    )
    lang = get_locale(request)
    await AppSetting.set("ui_language", lang)

    logger.info("Settings updated by %s", user.username)
    settings = await AppSetting.get_all()
    return templates.TemplateResponse(
        request,
        "settings.html",
        template_context(request, user=user, settings=settings, saved=True),
    )


@router.post("/test", response_class=HTMLResponse)
async def settings_test_telegram(
    request: Request,
    user: User | None = Depends(optional_user),
    telegram_bot_token: str = Form(""),
    telegram_chat_id: str = Form(""),
):
    if not user:
        return login_redirect()

    lang = get_locale(request)
    ok, message = await send_telegram_raw(
        telegram_bot_token,
        telegram_chat_id,
        translate("telegram.test_body", lang),
    )

    settings = await AppSetting.get_all()
    settings["telegram_bot_token"] = telegram_bot_token.strip()
    settings["telegram_chat_id"] = telegram_chat_id.strip()

    if ok:
        logger.info("Telegram test OK for user %s", user.username)
        return templates.TemplateResponse(
            request,
            "settings.html",
            template_context(request, user=user, settings=settings, test_ok=message),
        )

    logger.warning("Telegram test failed for user %s: %s", user.username, message)
    return templates.TemplateResponse(
        request,
        "settings.html",
        template_context(request, user=user, settings=settings, test_error=message),
    )
