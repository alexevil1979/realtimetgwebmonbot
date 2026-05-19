import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.bootstrap import seed_defaults
from app.config import LOG_LEVEL, SCHEDULER_ENABLED
from app.database import close_db, init_db
from app.routers import auth, dashboard, i18n, servers, settings
from app.services.scheduler import reload_all_schedules, start_scheduler, stop_scheduler

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    await seed_defaults()
    if SCHEDULER_ENABLED:
        start_scheduler()
        await reload_all_schedules()
        logger.info("Scheduler enabled")
    else:
        logger.info("Scheduler disabled (worker mode expected)")
    logger.info("Uptime monitor started")
    yield
    if SCHEDULER_ENABLED:
        stop_scheduler()
    await close_db()
    logger.info("Uptime monitor stopped")


app = FastAPI(
    title="Uptime Monitor",
    description="Lightweight server availability monitoring",
    lifespan=lifespan,
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(i18n.router)
app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(servers.router)
app.include_router(settings.router)


@app.get("/health")
async def health():
    return {"status": "ok"}
