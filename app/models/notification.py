from tortoise import fields, models

class Notification(models.Model):
    id = fields.IntField(primary_key=True)
    user = fields.ForeignKeyField("models.User", related_name="notifications")
    type = fields.CharField(max_length=50) # comment_reply, system, etc.
    title = fields.CharField(max_length=255)
    content = fields.TextField()
    is_read = fields.BooleanField(default=False)
    
    target_type = fields.CharField(max_length=50, null=True)
    target_id = fields.IntField(null=True)
    
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "notifications"
