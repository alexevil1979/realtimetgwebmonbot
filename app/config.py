import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-in-production")
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite://{DATA_DIR / 'uptime.db'}")
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
SCHEDULER_ENABLED = os.getenv("SCHEDULER_ENABLED", "true").lower() in (
    "1",
    "true",
    "yes",
)

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin")

SESSION_COOKIE = "uptime_session"
SESSION_MAX_AGE = 60 * 60 * 24 * 7  # 7 days

CHECK_HISTORY_LIMIT = 60
HTTP_OK_MIN = 200
HTTP_OK_MAX = 399

DEFAULT_LANG = os.getenv("DEFAULT_LANG", "ru")
