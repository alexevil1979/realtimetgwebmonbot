import logging

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from app.config import SESSION_COOKIE, SESSION_MAX_AGE
from app.i18n import get_locale, translate
from app.services.auth import authenticate, create_session_token, get_current_user
from app.templating import template_context, templates

logger = logging.getLogger(__name__)

router = APIRouter(tags=["auth"])


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    user = await get_current_user(request)
    if user:
        return RedirectResponse("/", status_code=303)
    lang = get_locale(request)
    return templates.TemplateResponse(
        request,
        "login.html",
        template_context(request, error=None),
    )


@router.post("/login")
async def login_submit(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
):
    lang = get_locale(request)
    user = await authenticate(username.strip(), password)
    if not user:
        logger.warning("Failed login attempt for user: %s", username)
        return templates.TemplateResponse(
            request,
            "login.html",
            template_context(
                request,
                error=translate("error.login_failed", lang),
            ),
            status_code=401,
        )

    response = RedirectResponse("/", status_code=303)
    response.set_cookie(
        SESSION_COOKIE,
        create_session_token(user.id),
        httponly=True,
        samesite="lax",
        max_age=SESSION_MAX_AGE,
    )
    logger.info("User %s logged in", user.username)
    return response


@router.post("/logout")
async def logout():
    response = RedirectResponse("/login", status_code=303)
    response.delete_cookie(SESSION_COOKIE)
    return response
