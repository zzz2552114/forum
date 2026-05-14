from tortoise import fields, models

from app.models.enums import ContentStatus, PostType

class Post(models.Model):
    id = fields.IntField(primary_key=True)
    title = fields.CharField(max_length=255)
    content = fields.TextField()
    post_type = fields.CharEnumField(PostType, default=PostType.DISCUSSION)
    status = fields.CharEnumField(ContentStatus, default=ContentStatus.PUBLISHED)
    
    author = fields.ForeignKeyField("models.User", related_name="posts")
    space = fields.ForeignKeyField("models.Space", related_name="posts")
    tags = fields.ManyToManyField("models.Tag", related_name="posts")
    
    is_pinned = fields.BooleanField(default=False)
    is_featured = fields.BooleanField(default=False)
    is_locked = fields.BooleanField(default=False)
    
    view_count = fields.IntField(default=0)
    like_count = fields.IntField(default=0)
    comment_count = fields.IntField(default=0)
    bookmark_count = fields.IntField(default=0)
    
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    
    class Meta:
        table = "posts"


class Comment(models.Model):
    id = fields.IntField(primary_key=True)
    content = fields.TextField()
    status = fields.CharEnumField(ContentStatus, default=ContentStatus.PUBLISHED)
    
    post = fields.ForeignKeyField("models.Post", related_name="comments")
    author = fields.ForeignKeyField("models.User", related_name="comments")
    
    # Nested replies
    parent = fields.ForeignKeyField("models.Comment", related_name="replies", null=True)
    
    like_count = fields.IntField(default=0)
    reply_count = fields.IntField(default=0)
    
    created_at = fields.DatetimeField(auto_now_add=True)
    
    class Meta:
        table = "comments"


class PostLike(models.Model):
    """ Table to track user likes so users can't like multiple times. """
    id = fields.IntField(primary_key=True)
    user = fields.ForeignKeyField("models.User", related_name="post_likes")
    post = fields.ForeignKeyField("models.Post", related_name="liked_by")
    
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "post_likes"
        unique_together = (("user_id", "post_id"),)
