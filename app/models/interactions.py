from tortoise import fields, models

class SpaceSubscription(models.Model):
    id = fields.IntField(primary_key=True)
    user = fields.ForeignKeyField("models.User", related_name="space_subscriptions")
    space = fields.ForeignKeyField("models.Space", related_name="subscribers")
    
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "space_subscriptions"
        unique_together = (("user_id", "space_id"),)

class PostBookmark(models.Model):
    id = fields.IntField(primary_key=True)
    user = fields.ForeignKeyField("models.User", related_name="post_bookmarks")
    post = fields.ForeignKeyField("models.Post", related_name="bookmarked_by")
    
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "post_bookmarks"
        unique_together = (("user_id", "post_id"),)

class PostSubscription(models.Model):
    id = fields.IntField(primary_key=True)
    user = fields.ForeignKeyField("models.User", related_name="post_subscriptions")
    post = fields.ForeignKeyField("models.Post", related_name="subscribers")
    
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "post_subscriptions"
        unique_together = (("user_id", "post_id"),)

class SpaceMaster(models.Model):
    id = fields.IntField(primary_key=True)
    user = fields.ForeignKeyField("models.User", related_name="master_of_spaces")
    space = fields.ForeignKeyField("models.Space", related_name="masters")
    
    assigned_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "space_masters"
        unique_together = (("user_id", "space_id"),)
