from tortoise import fields, models

from app.models.enums import ContentStatus

'''
学习资源表 (resources)
存储独立于帖子的学习资料、文件合集或文档。
'''
class Resource(models.Model):
    """ To handle attached files, documents, or course materials """
    id = fields.IntField(primary_key=True)
    title = fields.CharField(max_length=255, null=True)
    description = fields.TextField(null=True)
    
    filename = fields.CharField(max_length=255, null=True) # Cached from latest version
    resource_type = fields.CharField(max_length=50, null=True)
    status = fields.CharEnumField(ContentStatus, default=ContentStatus.PUBLISHED)
    
    uploader = fields.ForeignKeyField("models.User", related_name="resources")
    post = fields.ForeignKeyField("models.Post", related_name="resources", null=True)
    school_space = fields.ForeignKeyField("models.Space", related_name="school_resources", null=True)
    space = fields.ForeignKeyField("models.Space", related_name="resources", null=True)
    
    download_count = fields.IntField(default=0)
    bookmark_count = fields.IntField(default=0)
    
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "resources"

'''
资源版本控制表 (resource_versions)
存储某个学习资源的具体版本文件记录（支持更新迭代）。
'''
class ResourceVersion(models.Model):
    id = fields.IntField(primary_key=True)
    resource = fields.ForeignKeyField("models.Resource", related_name="versions")
    file = fields.ForeignKeyField("models.File", related_name="resource_versions")
    version_note = fields.CharField(max_length=255, null=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "resource_versions"
