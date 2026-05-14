from tortoise import fields, models

'''
板块订阅关联表 (space_subscriptions)
记录用户关注（加入）了哪些板块。
'''
class SpaceSubscription(models.Model):
    id = fields.IntField(primary_key=True)
    user = fields.ForeignKeyField("models.User", related_name="space_subscriptions")
    space = fields.ForeignKeyField("models.Space", related_name="subscribers")
    
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "space_subscriptions"
        unique_together = (("user_id", "space_id"),)

'''
帖子收藏关联表 (post_bookmarks)
记录用户收藏了哪些帖子。
'''
class PostBookmark(models.Model):
    id = fields.IntField(primary_key=True)
    user = fields.ForeignKeyField("models.User", related_name="post_bookmarks")
    post = fields.ForeignKeyField("models.Post", related_name="bookmarked_by")
    
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "post_bookmarks"
        unique_together = (("user_id", "post_id"),)

'''
帖子订阅关联表 (post_subscriptions)
记录用户订阅了哪些帖子（有新回复时会收到通知）。
'''
class PostSubscription(models.Model):
    id = fields.IntField(primary_key=True)
    user = fields.ForeignKeyField("models.User", related_name="post_subscriptions")
    post = fields.ForeignKeyField("models.Post", related_name="subscribers")
    
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "post_subscriptions"
        unique_together = (("user_id", "post_id"),)

'''
板块版主关联表 (space_masters)
记录哪些用户是哪些板块的版主（管理员）。
'''
class SpaceMaster(models.Model):
    id = fields.IntField(primary_key=True)
    user = fields.ForeignKeyField("models.User", related_name="master_of_spaces")
    space = fields.ForeignKeyField("models.Space", related_name="masters")
    
    assigned_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "space_masters"
        unique_together = (("user_id", "space_id"),)

'''
资源收藏关联表 (resource_bookmarks)
记录用户收藏了哪些学习资料/资源。
'''
class ResourceBookmark(models.Model):
    id = fields.IntField(primary_key=True)
    user = fields.ForeignKeyField("models.User", related_name="resource_bookmarks")
    resource = fields.ForeignKeyField("models.Resource", related_name="bookmarked_by")
    
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "resource_bookmarks"
        unique_together = (("user_id", "resource_id"),)

'''
资源下载关联表 (resource_downloads)
记录用户下载过哪些资源（可用于积分计算或去重检查）。
'''
class ResourceDownload(models.Model):
    id = fields.IntField(primary_key=True)
    user = fields.ForeignKeyField("models.User", related_name="resource_downloads")
    resource = fields.ForeignKeyField("models.Resource", related_name="downloaded_by")
    
    downloaded_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "resource_downloads"
