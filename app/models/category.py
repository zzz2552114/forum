from tortoise import fields, models

class Category(models.Model):
    """
    大分类表 (categories)
    比如：“学校”、“课程”、“爱好”等顶层分类。
    """
    id = fields.IntField(primary_key=True)
    name = fields.CharField(max_length=100, unique=True) # 分类名 e.g., 'Schools', 'Courses', 'Hobbies'
    description = fields.TextField(null=True)
    
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "categories"


from app.models.enums import SpaceType, ContentStatus

class Space(models.Model):
    """
    具体板块表 (spaces)
    大分类下的具体交流空间。比如“学校”大类下的“北京大学”板块。
    """
    id = fields.IntField(primary_key=True)
    name = fields.CharField(max_length=100) # 板块名 e.g., 'Peking University', 'Calculus'
    slug = fields.CharField(max_length=100, unique=True, null=True) # URL 友好别名 (如 peking-university)
    description = fields.TextField(null=True)
    type = fields.CharEnumField(SpaceType, default=SpaceType.COURSE) # 板块类型 (课程/活动等)
    status = fields.CharEnumField(ContentStatus, default=ContentStatus.PUBLISHED)
    
    category = fields.ForeignKeyField("models.Category", related_name="spaces") # 属于哪个大分类
    
    # Optionally, a space might have an owner/creator
    owner = fields.ForeignKeyField("models.User", related_name="owned_spaces", null=True) # 创建者（也是默认版主）
    
    # Cached metrics (统计缓存)
    post_count = fields.IntField(default=0) # 帖子总数
    resource_count = fields.IntField(default=0) # 资料总数
    subscriber_count = fields.IntField(default=0) # 关注总数
    
    created_at = fields.DatetimeField(auto_now_add=True)
    
    class Meta:
        table = "spaces"
        unique_together = (("name", "category_id"),) # 同一个大类下不能有同名的板块
