from tortoise import fields
from tortoise.models import Model


class Server(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=128)
    url = fields.CharField(max_length=512)
    timeout_sec = fields.IntField(default=10)
    interval_minutes = fields.IntField(default=5)
    enabled = fields.BooleanField(default=True)
    last_status = fields.CharField(max_length=16, null=True)  # up | down | unknown
    last_checked_at = fields.DatetimeField(null=True)
    last_response_ms = fields.IntField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    checks: fields.ReverseRelation["Check"]

    class Meta:
        table = "servers"
