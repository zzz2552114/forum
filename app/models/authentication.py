from tortoise import fields, models

class MailAuth(models.Model):
    id = fields.IntField(primary_key=True)
    code = fields.CharField(max_length=6)
    user = fields.ForeignKeyField("models.User", related_name="mail_auths")
    email = fields.CharField(max_length=150)
    school_name = fields.CharField(max_length=100)
    is_used = fields.BooleanField(default=False)
    attempts = fields.IntField(default=0)
    expired_at = fields.DatetimeField()
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "mail_auths"
