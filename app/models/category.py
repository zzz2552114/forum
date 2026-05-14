from tortoise import fields, models

class Category(models.Model):
    id = fields.IntField(primary_key=True)
    name = fields.CharField(max_length=100, unique=True) # e.g., 'Schools', 'Courses', 'Hobbies'
    description = fields.TextField(null=True)
    
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "categories"


from app.models.enums import SpaceType, ContentStatus

class Space(models.Model):
    id = fields.IntField(primary_key=True)
    name = fields.CharField(max_length=100) # e.g., 'Peking University', 'Calculus'
    slug = fields.CharField(max_length=100, unique=True, null=True)
    description = fields.TextField(null=True)
    type = fields.CharEnumField(SpaceType, default=SpaceType.COURSE)
    status = fields.CharEnumField(ContentStatus, default=ContentStatus.PUBLISHED)
    
    category = fields.ForeignKeyField("models.Category", related_name="spaces")
    
    # Optionally, a space might have an owner/creator
    owner = fields.ForeignKeyField("models.User", related_name="owned_spaces", null=True)
    
    # Cached metrics
    post_count = fields.IntField(default=0)
    resource_count = fields.IntField(default=0)
    subscriber_count = fields.IntField(default=0)
    
    created_at = fields.DatetimeField(auto_now_add=True)
    
    class Meta:
        table = "spaces"
        unique_together = (("name", "category_id"),)
