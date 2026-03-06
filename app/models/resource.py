from tortoise import fields, models

class Resource(models.Model):
    """ To handle attached files, documents, or course materials """
    id = fields.IntField(pk=True)
    filename = fields.CharField(max_length=255)
    file_url = fields.CharField(max_length=512)
    file_type = fields.CharField(max_length=50, null=True)
    
    uploader = fields.ForeignKeyField("models.User", related_name="resources")
    post = fields.ForeignKeyField("models.Post", related_name="resources", null=True)
    
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "resources"
