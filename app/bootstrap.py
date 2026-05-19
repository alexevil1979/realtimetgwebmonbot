import logging

from app.config import ADMIN_PASSWORD, ADMIN_USERNAME
from app.models import AppSetting, User
from app.models.setting import DEFAULTS
from app.services.auth import hash_password

logger = logging.getLogger(__name__)


async def seed_defaults() -> None:
    if not await User.exists():
        await User.create(
            username=ADMIN_USERNAME,
            password_hash=hash_password(ADMIN_PASSWORD),
        )
        logger.info("Created default admin user: %s", ADMIN_USERNAME)

    for key, value in DEFAULTS.items():
        if not await AppSetting.filter(key=key).exists():
            await AppSetting.set(key, value)
