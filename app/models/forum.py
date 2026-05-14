from tortoise import fields, models

from app.models.enums import ContentStatus, PostType

'''
帖子表 (posts)
论坛核心表，存储所有的帖子内容。
'''
class Post(models.Model):
    id = fields.IntField(primary_key=True)
    title = fields.CharField(max_length=255) # 帖子标题
    content = fields.TextField() # 帖子正文内容（可能包含 Markdown/HTML）
    post_type = fields.CharEnumField(PostType, default=PostType.DISCUSSION) # 帖子类型：讨论/提问等
    status = fields.CharEnumField(ContentStatus, default=ContentStatus.PUBLISHED) # 状态：已发布/被隐藏/草稿等
    
    # 关联外键 (Foreign Keys)
    author = fields.ForeignKeyField("models.User", related_name="posts") # 帖子作者
    space = fields.ForeignKeyField("models.Space", related_name="posts") # 所属的板块 (Space)
    tags = fields.ManyToManyField("models.Tag", related_name="posts") # 多对多关联：帖子带的标签
    
    # 状态标记
    is_pinned = fields.BooleanField(default=False) # 是否置顶
    is_featured = fields.BooleanField(default=False) # 是否被推荐/精华
    is_locked = fields.BooleanField(default=False) # 是否被锁定（禁止评论）
    
    # 数据统计缓存（避免每次 count 查全表）
    view_count = fields.IntField(default=0)
    like_count = fields.IntField(default=0)
    comment_count = fields.IntField(default=0)
    bookmark_count = fields.IntField(default=0)
    hot_score = fields.FloatField(default=0.0) # 热门分数，用于排序
    
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    
    class Meta:
        table = "posts"


'''
评论表 (comments)
存储帖子下的所有评论与子回复。
'''
class Comment(models.Model):
    id = fields.IntField(primary_key=True)
    content = fields.TextField() # 评论内容
    status = fields.CharEnumField(ContentStatus, default=ContentStatus.PUBLISHED)
    
    post = fields.ForeignKeyField("models.Post", related_name="comments") # 该评论属于哪个帖子
    author = fields.ForeignKeyField("models.User", related_name="comments") # 评论的作者
    
    # Nested replies (嵌套回复设计)
    # 如果 parent_id 为空，说明这是一级评论；如果不为空，说明是回复别人的二级/多级评论
    parent = fields.ForeignKeyField("models.Comment", related_name="replies", null=True)
    
    like_count = fields.IntField(default=0)
    reply_count = fields.IntField(default=0)
    
    created_at = fields.DatetimeField(auto_now_add=True)
    
    class Meta:
        table = "comments"


'''
帖子点赞记录表 (post_likes)
中间表，用于记录谁点赞了哪个帖子，确保一个用户对一个帖子只能点赞一次。
'''
class PostLike(models.Model):
    id = fields.IntField(primary_key=True)
    user = fields.ForeignKeyField("models.User", related_name="post_likes")
    post = fields.ForeignKeyField("models.Post", related_name="liked_by")
    
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "post_likes"
        unique_together = (("user_id", "post_id"),) # 联合唯一索引：一个用户对一个帖子只有一条点赞记录
