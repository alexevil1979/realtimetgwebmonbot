from tortoise import fields
from tortoise.models import Model


class Check(Model):
    id = fields.IntField(pk=True)
    server: fields.ForeignKeyRelation["Server"] = fields.ForeignKeyField(
        "models.Server", related_name="checks", on_delete=fields.CASCADE
    )
    is_up = fields.BooleanField()
    status_code = fields.IntField(null=True)
    response_ms = fields.IntField(null=True)
    error_message = fields.CharField(max_length=512, null=True)
    checked_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "checks"
        ordering = ["-checked_at"]
