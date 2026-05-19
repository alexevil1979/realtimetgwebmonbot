from tortoise import fields
from tortoise.models import Model

DEFAULTS = {
    "telegram_bot_token": "",
    "telegram_chat_id": "",
    "notify_on_up": "true",
    "notify_down_after_minutes": "15",
    "notify_cooldown_minutes": "15",
    "ui_language": "ru",
}


class AppSetting(Model):
    key = fields.CharField(max_length=64, pk=True)
    value = fields.TextField(default="")

    class Meta:
        table = "settings"

    @classmethod
    async def get_all(cls) -> dict[str, str]:
        rows = await cls.all()
        result = dict(DEFAULTS)
        for row in rows:
            result[row.key] = row.value
        return result

    @classmethod
    async def get(cls, key: str, default: str = "") -> str:
        row = await cls.filter(key=key).first()
        if row:
            return row.value
        return DEFAULTS.get(key, default)

    @classmethod
    async def set(cls, key: str, value: str) -> None:
        await cls.update_or_create(defaults={"value": value}, key=key)
