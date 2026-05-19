from tortoise import Tortoise

from app.config import DATABASE_URL

TORTOISE_ORM = {
    "connections": {"default": DATABASE_URL},
    "apps": {
        "models": {
            "models": ["app.models"],
            "default_connection": "default",
        }
    },
}


async def init_db() -> None:
    from app.migrate import run_migrations

    await Tortoise.init(config=TORTOISE_ORM)
    await Tortoise.generate_schemas()
    await run_migrations()


async def close_db() -> None:
    await Tortoise.close_connections()
