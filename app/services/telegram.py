import logging
from datetime import datetime, timedelta, timezone

import httpx

from app.models import AppSetting, Server

logger = logging.getLogger(__name__)

_last_notify: dict[int, datetime] = {}


async def _get_settings() -> dict[str, str]:
    return await AppSetting.get_all()


async def send_telegram_raw(token: str, chat_id: str, text: str) -> tuple[bool, str]:
    token = token.strip()
    chat_id = chat_id.strip()
    if not token or not chat_id:
        return False, "Укажите Bot Token и Chat ID"

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(
                url,
                json={"chat_id": chat_id, "text": text, "parse_mode": "HTML"},
            )
            if resp.status_code != 200:
                detail = resp.text[:300]
                try:
                    detail = resp.json().get("description", detail)
                except Exception:
                    pass
                logger.warning("Telegram API error: %s %s", resp.status_code, detail)
                return False, str(detail)
            return True, "Сообщение отправлено в Telegram"
    except Exception as exc:
        logger.exception("Failed to send Telegram message: %s", exc)
        return False, str(exc)


async def send_telegram(text: str) -> bool:
    settings = await _get_settings()
    token = settings.get("telegram_bot_token", "")
    chat_id = settings.get("telegram_chat_id", "")
    ok, _ = await send_telegram_raw(token, chat_id, text)
    if not ok and not token.strip():
        logger.debug("Telegram not configured, skip notification")
    return ok


def _cooldown_passed(server_id: int, cooldown_minutes: int) -> bool:
    last = _last_notify.get(server_id)
    if not last:
        return True
    return datetime.now(timezone.utc) - last >= timedelta(minutes=cooldown_minutes)


async def notify_status_change(
    server: Server,
    old_status: str | None,
    new_status: str,
    error_message: str | None = None,
) -> None:
    settings = await _get_settings()
    cooldown = int(settings.get("notify_cooldown_minutes", "15") or "15")
    notify_on_up = settings.get("notify_on_up", "true").lower() in ("1", "true", "yes")

    if new_status == old_status:
        return

    if new_status == "up" and not notify_on_up:
        return

    if not _cooldown_passed(server.id, cooldown):
        logger.info("Telegram cooldown active for server %s", server.id)
        return

    if new_status == "down":
        text = (
            f"🔴 <b>DOWN</b>: {server.name}\n"
            f"URL: {server.url}\n"
            f"{error_message or 'Check failed'}"
        )
    else:
        ms = server.last_response_ms
        ms_str = f"{ms} ms" if ms is not None else "—"
        text = (
            f"🟢 <b>UP</b>: {server.name}\n"
            f"URL: {server.url}\n"
            f"Response: {ms_str}"
        )

    if await send_telegram(text):
        _last_notify[server.id] = datetime.now(timezone.utc)
        logger.info("Telegram notification sent for server %s (%s)", server.id, new_status)
