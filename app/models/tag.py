from tortoise import fields, models

class Tag(models.Model):
    id = fields.IntField(primary_key=True)
    name = fields.CharField(max_length=50, unique=True)
    slug = fields.CharField(max_length=50, unique=True, null=True)
    
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "tags"
