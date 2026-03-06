from tortoise import fields, models

from app.models.enums import ContentStatus

class Resource(models.Model):
    """ To handle attached files, documents, or course materials """
    id = fields.IntField(primary_key=True)
    title = fields.CharField(max_length=255, null=True)
    description = fields.TextField(null=True)
    
    filename = fields.CharField(max_length=255)
    file_url = fields.CharField(max_length=512)
    resource_type = fields.CharField(max_length=50, null=True)
    status = fields.CharEnumField(ContentStatus, default=ContentStatus.PUBLISHED)
    
    uploader = fields.ForeignKeyField("models.User", related_name="resources")
    post = fields.ForeignKeyField("models.Post", related_name="resources", null=True)
    space = fields.ForeignKeyField("models.Space", related_name="resources", null=True)
    
    download_count = fields.IntField(default=0)
    bookmark_count = fields.IntField(default=0)
    
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "resources"
