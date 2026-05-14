from tortoise import fields, models

'''
消息通知表 (notifications)
存储系统的各类通知（如有人回复、点赞、系统通告等）。
'''
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
