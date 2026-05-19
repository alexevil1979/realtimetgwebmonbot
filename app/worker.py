"""Standalone scheduler worker (no web UI). Run: python -m app.worker"""
import asyncio
import logging
import signal

from app.bootstrap import seed_defaults
from app.config import LOG_LEVEL
from app.database import close_db, init_db
from app.services.scheduler import reload_all_schedules, scheduler, start_scheduler, stop_scheduler

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


async def main() -> None:
    await init_db()
    await seed_defaults()
    start_scheduler()
    await reload_all_schedules()
    logger.info("Worker running — press Ctrl+C to stop")

    stop_event = asyncio.Event()

    def _shutdown(*_args):
        stop_event.set()

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, _shutdown)
        except NotImplementedError:
            pass

    await stop_event.wait()
    stop_scheduler()
    await close_db()
    logger.info("Worker stopped")


if __name__ == "__main__":
    asyncio.run(main())
