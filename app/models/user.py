from tortoise import fields, models

from app.models.enums import UserRole, TrustLevel, SchoolVisibility

class User(models.Model):
    id = fields.IntField(primary_key=True)
    username = fields.CharField(max_length=50, unique=True, db_index=True)
    email = fields.CharField(max_length=150, unique=True, db_index=True)
    hashed_password = fields.CharField(max_length=255)
    
    # Profile & Extended Info
    nickname = fields.CharField(max_length=50, null=True)
    avatar_url = fields.CharField(max_length=255, null=True)
    bio = fields.TextField(null=True)
    school_name = fields.CharField(max_length=100, null=True)
    school_visibility = fields.CharEnumField(SchoolVisibility, default=SchoolVisibility.PUBLIC)
    
    # Roles and Permissions
    role = fields.CharEnumField(UserRole, default=UserRole.USER)
    trust_level = fields.IntEnumField(TrustLevel, default=TrustLevel.BASIC)
    reputation_score = fields.IntField(default=0)
    
    is_active = fields.BooleanField(default=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "users"
