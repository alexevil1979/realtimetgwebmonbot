import logging

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from app.dependencies import login_redirect, optional_user
from app.i18n import get_locale, translate
from app.models import Server, User
from app.services.checker import run_check
from app.services.scheduler import schedule_server, unschedule_server
from app.templating import template_context, templates

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/servers", tags=["servers"])


@router.get("/new", response_class=HTMLResponse)
async def server_new(request: Request, user: User | None = Depends(optional_user)):
    if not user:
        return login_redirect()
    return templates.TemplateResponse(
        request,
        "server_form.html",
        template_context(request, user=user, server=None, error=None),
    )


@router.get("/{server_id}/edit", response_class=HTMLResponse)
async def server_edit(
    request: Request,
    server_id: int,
    user: User | None = Depends(optional_user),
):
    if not user:
        return login_redirect()
    server = await Server.filter(id=server_id).first()
    if not server:
        return RedirectResponse("/", status_code=303)
    return templates.TemplateResponse(
        request,
        "server_form.html",
        template_context(request, user=user, server=server, error=None),
    )


@router.post("/create")
async def server_create(
    request: Request,
    user: User | None = Depends(optional_user),
    name: str = Form(...),
    url: str = Form(...),
    timeout_sec: int = Form(10),
    interval_minutes: int = Form(5),
    enabled: str | None = Form(None),
):
    if not user:
        return login_redirect()

    lang = get_locale(request)
    url = url.strip()
    if not url.startswith(("http://", "https://")):
        return templates.TemplateResponse(
            request,
            "server_form.html",
            template_context(
                request,
                user=user,
                server=None,
                error=translate("error.url_scheme", lang),
            ),
            status_code=400,
        )

    server = await Server.create(
        name=name.strip(),
        url=url,
        timeout_sec=max(1, min(timeout_sec, 120)),
        interval_minutes=max(1, min(interval_minutes, 1440)),
        enabled=enabled == "on",
        last_status="unknown",
    )
    await schedule_server(server)
    logger.info("Created server %s: %s", server.id, server.name)
    return RedirectResponse("/", status_code=303)


@router.post("/{server_id}/update")
async def server_update(
    request: Request,
    server_id: int,
    user: User | None = Depends(optional_user),
    name: str = Form(...),
    url: str = Form(...),
    timeout_sec: int = Form(10),
    interval_minutes: int = Form(5),
    enabled: str | None = Form(None),
):
    if not user:
        return login_redirect()

    lang = get_locale(request)
    server = await Server.filter(id=server_id).first()
    if not server:
        return RedirectResponse("/", status_code=303)

    url = url.strip()
    if not url.startswith(("http://", "https://")):
        return templates.TemplateResponse(
            request,
            "server_form.html",
            template_context(
                request,
                user=user,
                server=server,
                error=translate("error.url_scheme", lang),
            ),
            status_code=400,
        )

    server.name = name.strip()
    server.url = url
    server.timeout_sec = max(1, min(timeout_sec, 120))
    server.interval_minutes = max(1, min(interval_minutes, 1440))
    server.enabled = enabled == "on"
    await server.save()

    await unschedule_server(server.id)
    if server.enabled:
        await schedule_server(server)

    logger.info("Updated server %s", server.id)
    return RedirectResponse("/", status_code=303)


@router.post("/{server_id}/delete")
async def server_delete(
    server_id: int,
    user: User | None = Depends(optional_user),
):
    if not user:
        return login_redirect()

    await unschedule_server(server_id)
    deleted = await Server.filter(id=server_id).delete()
    if deleted:
        logger.info("Deleted server %s", server_id)
    return RedirectResponse("/", status_code=303)


@router.post("/{server_id}/check-now")
async def server_check_now(
    server_id: int,
    user: User | None = Depends(optional_user),
):
    if not user:
        return login_redirect()
    await run_check(server_id)
    return RedirectResponse("/", status_code=303)
