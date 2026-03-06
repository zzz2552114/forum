from tortoise import fields, models

class Post(models.Model):
    id = fields.IntField(pk=True)
    title = fields.CharField(max_length=255)
    content = fields.TextField()
    
    author = fields.ForeignKeyField("models.User", related_name="posts")
    space = fields.ForeignKeyField("models.Space", related_name="posts")
    
    view_count = fields.IntField(default=0)
    like_count = fields.IntField(default=0)
    
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    
    class Meta:
        table = "posts"


class Comment(models.Model):
    id = fields.IntField(pk=True)
    content = fields.TextField()
    
    post = fields.ForeignKeyField("models.Post", related_name="comments")
    author = fields.ForeignKeyField("models.User", related_name="comments")
    
    # Optionally support nested replies
    parent = fields.ForeignKeyField("models.Comment", related_name="replies", null=True)
    
    created_at = fields.DatetimeField(auto_now_add=True)
    
    class Meta:
        table = "comments"


class PostLike(models.Model):
    """ Table to track user likes so users can't like multiple times. """
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField("models.User", related_name="post_likes")
    post = fields.ForeignKeyField("models.Post", related_name="liked_by")
    
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "post_likes"
        unique_together = (("user_id", "post_id"),)
