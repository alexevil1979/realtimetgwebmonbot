import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.models import Server
from app.services.checker import run_check

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()
JOB_PREFIX = "check_server_"


def _job_id(server_id: int) -> str:
    return f"{JOB_PREFIX}{server_id}"


async def schedule_server(server: Server) -> None:
    job_id = _job_id(server.id)
    if scheduler.get_job(job_id):
        scheduler.remove_job(job_id)

    if not server.enabled:
        logger.debug("Server %s disabled, not scheduled", server.id)
        return

    minutes = max(1, server.interval_minutes)
    scheduler.add_job(
        run_check,
        trigger=IntervalTrigger(minutes=minutes),
        args=[server.id],
        id=job_id,
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )
    logger.info("Scheduled server %s every %s min", server.id, minutes)
    # Run first check soon after scheduling
    scheduler.add_job(
        run_check,
        args=[server.id],
        id=f"{job_id}_initial",
        replace_existing=True,
        max_instances=1,
    )


async def unschedule_server(server_id: int) -> None:
    for suffix in ("", "_initial"):
        job_id = f"{_job_id(server_id)}{suffix}"
        if scheduler.get_job(job_id):
            scheduler.remove_job(job_id)


async def reload_all_schedules() -> None:
    for job in scheduler.get_jobs():
        if job.id.startswith(JOB_PREFIX):
            scheduler.remove_job(job.id)

    servers = await Server.filter(enabled=True).all()
    for server in servers:
        await schedule_server(server)
    logger.info("Reloaded schedules for %s servers", len(servers))


def start_scheduler() -> None:
    if not scheduler.running:
        scheduler.start()
        logger.info("APScheduler started")


def stop_scheduler() -> None:
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("APScheduler stopped")
