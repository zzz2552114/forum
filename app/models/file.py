from tortoise import fields, models

class File(models.Model):
    id = fields.IntField(primary_key=True)
    filename = fields.CharField(max_length=255)
    content_type = fields.CharField(max_length=100)
    size = fields.IntField()  # size in bytes
    url = fields.CharField(max_length=1024)
    biz_type = fields.CharField(max_length=50, null=True)  # resource, avatar, attachment
    
    uploader = fields.ForeignKeyField("models.User", related_name="uploaded_files")
    
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "files"
