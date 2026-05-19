import logging
from datetime import datetime, timedelta, timezone

import httpx

from app.models import AppSetting, Server

logger = logging.getLogger(__name__)

_last_notify: dict[int, datetime] = {}


async def _get_settings() -> dict[str, str]:
    return await AppSetting.get_all()


def _aware(dt: datetime | None) -> datetime | None:
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


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


async def _send_down_alert(
    server: Server,
    error_message: str | None,
    down_minutes: int,
) -> None:
    text = (
        f"🔴 <b>DOWN</b>: {server.name}\n"
        f"URL: {server.url}\n"
        f"Недоступен более {down_minutes} мин\n"
        f"{error_message or 'Проверка не прошла'}"
    )
    if await send_telegram(text):
        _last_notify[server.id] = datetime.now(timezone.utc)
        logger.info("Telegram DOWN alert for server %s (%s min)", server.id, down_minutes)


async def _send_up_alert(server: Server) -> None:
    ms = server.last_response_ms
    ms_str = f"{ms} ms" if ms is not None else "—"
    text = (
        f"🟢 <b>UP</b>: {server.name}\n"
        f"URL: {server.url}\n"
        f"Снова доступен, отклик: {ms_str}"
    )
    if await send_telegram(text):
        _last_notify[server.id] = datetime.now(timezone.utc)
        logger.info("Telegram UP alert for server %s", server.id)


async def evaluate_telegram_alerts(
    server: Server,
    is_up: bool,
    error_message: str | None,
    checked_at: datetime,
) -> None:
    """DOWN — только после N минут подряд без ответа. UP — после восстановления."""
    settings = await _get_settings()
    down_after = int(settings.get("notify_down_after_minutes", "15") or "15")
    cooldown = int(settings.get("notify_cooldown_minutes", "15") or "15")
    notify_on_up = settings.get("notify_on_up", "true").lower() in ("1", "true", "yes")

    now = _aware(checked_at) or datetime.now(timezone.utc)

    if is_up:
        was_alerted = server.alert_down_sent
        server.down_since = None
        server.alert_down_sent = False
        await server.save(update_fields=["down_since", "alert_down_sent"])

        if was_alerted and notify_on_up and _cooldown_passed(server.id, cooldown):
            await _send_up_alert(server)
        return

    if server.down_since is None:
        server.down_since = now
        await server.save(update_fields=["down_since"])

    down_since = _aware(server.down_since)
    if down_since is None:
        return

    elapsed_min = int((now - down_since).total_seconds() // 60)
    if elapsed_min < down_after:
        logger.debug(
            "Server %s down %s min, alert after %s min",
            server.id,
            elapsed_min,
            down_after,
        )
        return

    if server.alert_down_sent:
        return

    if not _cooldown_passed(server.id, cooldown):
        logger.info("Telegram cooldown active for server %s", server.id)
        return

    await _send_down_alert(server, error_message, elapsed_min)
    server.alert_down_sent = True
    await server.save(update_fields=["alert_down_sent"])
