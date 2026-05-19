import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.dependencies import login_redirect, optional_user
from app.models import Server, User
from app.services.checker import calc_uptime

logger = logging.getLogger(__name__)

router = APIRouter(tags=["dashboard"])
templates = Jinja2Templates(directory="app/templates")


def _format_dt(dt: datetime | None) -> str:
    if not dt:
        return "—"
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone().strftime("%d.%m.%Y %H:%M:%S")


@router.get("/", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    user: User | None = Depends(optional_user),
):
    if not user:
        return login_redirect()

    servers = await Server.all().order_by("name")
    items = []
    for s in servers:
        uptime_24h = await calc_uptime(s.id, 24)
        uptime_7d = await calc_uptime(s.id, 24 * 7)
        items.append(
            {
                "server": s,
                "uptime_24h": uptime_24h,
                "uptime_7d": uptime_7d,
                "last_checked": _format_dt(s.last_checked_at),
            }
        )

    return templates.TemplateResponse(
        request,
        "dashboard.html",
        {
            "request": request,
            "user": user,
            "items": items,
        },
    )
