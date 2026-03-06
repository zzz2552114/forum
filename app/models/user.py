from tortoise import fields, models

class User(models.Model):
    id = fields.IntField(pk=True)
    username = fields.CharField(max_length=50, unique=True, index=True)
    email = fields.CharField(max_length=150, unique=True, index=True)
    hashed_password = fields.CharField(max_length=255)
    
    # Roles can be 'admin', 'moderator', 'user'
    role = fields.CharField(max_length=20, default="user")
    
    is_active = fields.BooleanField(default=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "users"
