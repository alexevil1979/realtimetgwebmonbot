import logging

from tortoise import Tortoise

logger = logging.getLogger(__name__)

_SERVER_COLUMNS = (
    ("down_since", "TIMESTAMP"),
    ("alert_down_sent", "INTEGER DEFAULT 0"),
)


async def run_migrations() -> None:
    conn = Tortoise.get_connection("default")
    _, rows = await conn.execute_query("PRAGMA table_info(servers)")
    existing = {row[1] for row in rows}

    for name, col_type in _SERVER_COLUMNS:
        if name in existing:
            continue
        sql = f"ALTER TABLE servers ADD COLUMN {name} {col_type}"
        await conn.execute_query(sql)
        logger.info("Migration: added servers.%s", name)
