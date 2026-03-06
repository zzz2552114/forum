from tortoise import fields, models

class Category(models.Model):
    id = fields.IntField(primary_key=True)
    name = fields.CharField(max_length=100, unique=True) # e.g., 'Schools', 'Courses', 'Hobbies'
    description = fields.TextField(null=True)
    
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "categories"


class Space(models.Model):
    id = fields.IntField(primary_key=True)
    name = fields.CharField(max_length=100) # e.g., 'Peking University', 'Calculus'
    description = fields.TextField(null=True)
    
    category = fields.ForeignKeyField("models.Category", related_name="spaces")
    
    # Optionally, a space might have an owner/moderator
    owner = fields.ForeignKeyField("models.User", related_name="owned_spaces", null=True)
    
    created_at = fields.DatetimeField(auto_now_add=True)
    
    class Meta:
        table = "spaces"
        unique_together = (("name", "category_id"),)
