from tortoise import fields, models

'''
标签表 (tags)
存储所有的系统标签或用户自定义标签（如“求助”、“技术分享”）。
'''
class Tag(models.Model):
    id = fields.IntField(primary_key=True)
    name = fields.CharField(max_length=50, unique=True)
    slug = fields.CharField(max_length=50, unique=True, null=True)
    
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "tags"
