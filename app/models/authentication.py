from tortoise import fields, models

class MailAuth(models.Model):
    id = fields.IntField(pk=True)
    code = fields.CharField(max_length=6)
    user = fields.ForeignKeyField("models.User", related_name="mail_auths")
    email = fields.CharField(max_length=150)
    school_name = fields.CharField(max_length=100)
    
    attempts = fields.IntField(default=0) # 尝试次数
    created_at = fields.DatetimeField(auto_now_add=True)
    expired_at = fields.DatetimeField()
    is_used = fields.BooleanField(default=False)

    class Meta:
        table = "mail_auths"
