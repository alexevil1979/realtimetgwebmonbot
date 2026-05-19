import logging
import time
from datetime import datetime, timedelta, timezone

import httpx

from app.config import CHECK_HISTORY_LIMIT, HTTP_OK_MAX, HTTP_OK_MIN
from app.models import Check, Server
from app.services.telegram import evaluate_telegram_alerts

logger = logging.getLogger(__name__)


async def run_check(server_id: int) -> None:
    server = await Server.filter(id=server_id).first()
    if not server or not server.enabled:
        return

    is_up = False
    status_code: int | None = None
    response_ms: int | None = None
    error_message: str | None = None

    start = time.perf_counter()
    try:
        async with httpx.AsyncClient(
            follow_redirects=True,
            timeout=httpx.Timeout(server.timeout_sec, connect=server.timeout_sec),
        ) as client:
            resp = await client.get(server.url)
            status_code = resp.status_code
            is_up = HTTP_OK_MIN <= status_code <= HTTP_OK_MAX
            if not is_up:
                error_message = f"HTTP {status_code}"
    except httpx.TimeoutException:
        error_message = "Timeout"
    except httpx.RequestError as exc:
        error_message = str(exc)[:500]
    except Exception as exc:
        logger.exception("Unexpected check error for server %s", server_id)
        error_message = str(exc)[:500]
    finally:
        response_ms = int((time.perf_counter() - start) * 1000)

    new_status = "up" if is_up else "down"
    now = datetime.now(timezone.utc)

    await Check.create(
        server_id=server.id,
        is_up=is_up,
        status_code=status_code,
        response_ms=response_ms,
        error_message=error_message,
    )

    prev_status = server.last_status
    server.last_status = new_status
    server.last_checked_at = now
    server.last_response_ms = response_ms
    await server.save()

    await _trim_history(server.id)

    if prev_status != new_status:
        logger.info(
            "Server %s (%s) status: %s -> %s",
            server.id,
            server.name,
            prev_status,
            new_status,
        )

    await evaluate_telegram_alerts(server, is_up, error_message, now)


async def _trim_history(server_id: int) -> None:
    checks = (
        await Check.filter(server_id=server_id)
        .order_by("-checked_at")
        .offset(CHECK_HISTORY_LIMIT)
    )
    if not checks:
        return
    ids = [c.id for c in checks]
    await Check.filter(id__in=ids).delete()


async def calc_uptime(server_id: int, hours: int) -> float | None:
    since = datetime.now(timezone.utc) - timedelta(hours=hours)
    checks = await Check.filter(server_id=server_id, checked_at__gte=since).all()
    if not checks:
        return None
    up_count = sum(1 for c in checks if c.is_up)
    return round(100.0 * up_count / len(checks), 2)
