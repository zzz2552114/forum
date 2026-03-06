from tortoise import fields, models

class Report(models.Model):
    """ For users reporting posts/comments or other users for moderation """
    id = fields.IntField(pk=True)
    reporter = fields.ForeignKeyField("models.User", related_name="reports_made")
    
    # Polymorphic-ish fields. Let's keep it simple by optionally linking
    post = fields.ForeignKeyField("models.Post", related_name="reports", null=True)
    comment = fields.ForeignKeyField("models.Comment", related_name="reports", null=True)
    
    reason = fields.TextField()
    status = fields.CharField(max_length=20, default="pending") # pending, reviewed, dismissed
    
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "reports"
