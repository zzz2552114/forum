from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import (
    AuthPrincipal,
    build_authorization_snapshot,
    ensure_min_trust,
    get_current_active_user,
    get_optional_principal,
)
from app.core.responses import paginate_response, success_response
from app.models.enums import SchoolVisibility, TrustLevel
from app.models.notification import Notification
from app.models.user import User
from app.schemas.common import PaginationData, ResponseBase
from app.schemas.notification import (
    NotificationMarkReadRequest,
    NotificationResponse,
    NotificationUnreadCountResponse,
)
from app.schemas.profile import UserPrivacyUpdate, UserProfileBase, UserProfileResponse
from app.schemas.me import MyStatsResponse, MyCommentItemResponse
from app.schemas.forum import PostResponse
from app.models.forum import Post, Comment, PostLike
from app.models.interactions import SpaceSubscription
from app.models.resource import Resource

router = APIRouter()


# ==========================================
# 获取当前登录用户自己的个人资料
# ==========================================
@router.get("/", response_model=ResponseBase[UserProfileResponse])
async def read_my_profile(current_user: User = Depends(get_current_active_user)) -> Any:
    return success_response(current_user)


# ==========================================
# 获取当前用户的详细权限快照 (前端用于鉴权控制按钮显示)
# ==========================================
@router.get("/authorization", response_model=ResponseBase[dict])
async def read_my_authorization(principal: AuthPrincipal = Depends(get_optional_principal)) -> Any:
    snapshot = await build_authorization_snapshot(principal)
    return success_response(snapshot)


# ==========================================
# 修改个人资料 (如修改昵称、头像、简介等)
# ==========================================
@router.patch("/profile", response_model=ResponseBase[UserProfileResponse])
async def update_my_profile(
    profile_in: UserProfileBase,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    update_data = profile_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(current_user, field, value)

    await current_user.save()
    return success_response(current_user)


# ==========================================
# 修改隐私设置 (如学校信息是否对外公开)
# ==========================================
@router.patch("/privacy", response_model=ResponseBase[UserProfileResponse])
async def update_my_privacy(
    privacy_in: UserPrivacyUpdate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    if privacy_in.school_visibility == SchoolVisibility.HIDDEN:
        ensure_min_trust(
            current_user,
            min_level=TrustLevel.VERIFIED,
            required_permission="user.hidden_school.view",
        )

    if privacy_in.school_visibility is not None:
        current_user.school_visibility = privacy_in.school_visibility

    await current_user.save()
    return success_response(current_user)


# ==========================================
# 分页获取我的系统通知列表
# ==========================================
@router.get("/notifications", response_model=ResponseBase[PaginationData[NotificationResponse]])
async def read_my_notifications(
    page: int = 1,
    page_size: int = 20,
    current_user: User = Depends(get_current_active_user),
):
    query = Notification.filter(user_id=current_user.id).order_by("-created_at")
    total = await query.count()
    skip = (page - 1) * page_size
    notifications = await query.offset(skip).limit(page_size)

    return paginate_response(notifications, page, page_size, total)


# ==========================================
# 获取未读通知的数量 (常用于前端导航栏小红点)
# ==========================================
@router.get("/notifications/unread-count", response_model=ResponseBase[NotificationUnreadCountResponse])
async def read_unread_notification_count(current_user: User = Depends(get_current_active_user)):
    unread_count = await Notification.filter(user_id=current_user.id, is_read=False).count()
    return success_response(NotificationUnreadCountResponse(unread_count=unread_count))


# ==========================================
# 将单条通知标记为已读
# ==========================================
@router.patch("/notifications/{notification_id}/read", response_model=ResponseBase[NotificationResponse])
async def read_notification(
    notification_id: int,
    current_user: User = Depends(get_current_active_user),
):
    notif = await Notification.get_or_none(id=notification_id, user_id=current_user.id)
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")

    notif.is_read = True
    await notif.save(update_fields=["is_read"])
    return success_response(notif)


# ==========================================
# 批量将通知标记为已读
# ==========================================
@router.patch("/notifications/read", response_model=ResponseBase[dict])
async def mark_notifications_as_read(
    payload: NotificationMarkReadRequest,
    current_user: User = Depends(get_current_active_user),
):
    query = Notification.filter(user_id=current_user.id, is_read=False)
    if payload.notification_ids:
        query = query.filter(id__in=payload.notification_ids)

    updated = await query.update(is_read=True)
    return success_response({"updated": updated})


@router.post("/notifications/read", response_model=ResponseBase[dict])
async def mark_notifications_as_read_legacy(
    payload: NotificationMarkReadRequest,
    current_user: User = Depends(get_current_active_user),
):
    return await mark_notifications_as_read(payload, current_user)


# ==========================================
# 获取我的数据统计 (发帖数、资源数、关注数等)
# ==========================================
@router.get("/stats", response_model=ResponseBase[MyStatsResponse])
async def read_my_stats(current_user: User = Depends(get_current_active_user)):
    joined_spaces_count = await SpaceSubscription.filter(user_id=current_user.id).count()
    post_count = await Post.filter(author_id=current_user.id).count()
    resource_count = await Resource.filter(uploader_id=current_user.id).count()
    
    # follower/following not fully implemented yet in the backend models, defaulting to 0 for now as per plan
    follower_count = 0 
    following_count = 0
    
    return success_response(MyStatsResponse(
        joined_spaces_count=joined_spaces_count,
        post_count=post_count,
        resource_count=resource_count,
        follower_count=follower_count,
        following_count=following_count
    ))


# ==========================================
# 获取我发出的所有评论记录
# ==========================================
@router.get("/comments", response_model=ResponseBase[PaginationData[MyCommentItemResponse]])
async def read_my_comments(
    page: int = 1,
    page_size: int = 20,
    current_user: User = Depends(get_current_active_user)
):
    query = Comment.filter(author_id=current_user.id).order_by("-created_at")
    total = await query.count()
    skip = (page - 1) * page_size
    comments = await query.offset(skip).limit(page_size).prefetch_related("post", "post__space")
    
    response_items = []
    for comment in comments:
        post = comment.post
        space = post.space if post else None
        
        post_payload = None
        space_payload = None
        
        if post:
            post_payload = {
                "id": post.id,
                "title": post.title,
                "content": post.content,
                "space_id": post.space_id
            }
        
        if space:
            space_payload = {
                "id": space.id,
                "name": space.name
            }
            
        response_items.append(MyCommentItemResponse(
            id=comment.id,
            content=comment.content,
            created_at=comment.created_at,
            post_id=comment.post_id,
            post=post_payload,
            space=space_payload
        ))

    return paginate_response(response_items, page, page_size, total)


# ==========================================
# 获取我点赞过的帖子列表
# ==========================================
@router.get("/likes", response_model=ResponseBase[PaginationData[PostResponse]])
async def read_my_likes(
    page: int = 1,
    page_size: int = 20,
    current_user: User = Depends(get_current_active_user)
):
    # Get the post IDs the user has liked
    query = PostLike.filter(user_id=current_user.id).order_by("-created_at")
    total = await query.count()
    skip = (page - 1) * page_size
    likes = await query.offset(skip).limit(page_size).prefetch_related("post", "post__author", "post__space", "post__tags")
    
    response_posts = []
    for like in likes:
        p = like.post
        if p:
            response_posts.append(PostResponse(
                id=p.id,
                title=p.title,
                content=p.content,
                space_id=p.space_id,
                author_id=p.author_id,
                author={"id": p.author.id, "username": p.author.username, "nickname": p.author.nickname, "avatar_url": p.author.avatar_url} if p.author else None,
                space={"id": p.space.id, "name": p.space.name} if p.space else None,
                view_count=p.view_count,
                like_count=p.like_count,
                comment_count=p.comment_count,
                bookmark_count=p.bookmark_count,
                created_at=p.created_at,
                updated_at=p.updated_at,
                tags=list(p.tags) if hasattr(p, "tags") else []
            ))

    return paginate_response(response_posts, page, page_size, total)
