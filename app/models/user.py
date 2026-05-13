from tortoise import fields, models

from app.models.enums import UserRole, TrustLevel, SchoolVisibility

class User(models.Model):
    """
    用户表 (users)
    核心业务表，存储所有用户的基本信息、权限角色以及偏好设置。
    """
    id = fields.IntField(primary_key=True) # 主键 ID
    username = fields.CharField(max_length=50, unique=True, db_index=True) # 登录用户名，唯一且加索引
    email = fields.CharField(max_length=150, unique=True, db_index=True) # 注册邮箱，唯一且加索引
    hashed_password = fields.CharField(max_length=255) # 加密后的密码哈希值
    
    # Profile & Extended Info (个人主页与扩展信息)
    nickname = fields.CharField(max_length=50, null=True) # 展示用的昵称
    avatar_url = fields.CharField(max_length=255, null=True) # 头像链接
    bio = fields.TextField(null=True) # 个人简介
    school_name = fields.CharField(max_length=100, null=True) # 学校名称
    school_visibility = fields.CharEnumField(SchoolVisibility, default=SchoolVisibility.PUBLIC) # 学校信息公开范围（公开/隐藏）
    
    # Roles and Permissions (角色与权限控制)
    role = fields.CharEnumField(UserRole, default=UserRole.USER) # 系统角色 (如 USER, ADMIN)
    trust_level = fields.IntEnumField(TrustLevel, default=TrustLevel.BASIC) # 信任等级 (影响发帖、传文件等权限)
    reputation_score = fields.IntField(default=0) # 社区声望积分
    
    is_active = fields.BooleanField(default=True) # 账号是否被激活 (被封号的话设为 False)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    
    # AI Preferences (AI助手相关配置)
    ai_api_key = fields.CharField(max_length=255, null=True) # 用户自带的 AI API Key
    ai_model = fields.CharField(max_length=50, null=True, default="qwen-plus") # 首选的大模型

    class Meta:
        table = "users"
