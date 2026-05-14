from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from tortoise.expressions import F

from app.api.deps import (
    ensure_min_trust,
    ensure_space_master_or_admin,
    get_current_active_user,
)
from app.core.responses import success_response
from app.models.enums import TrustLevel
from app.models.forum import Post, PostLike
from app.models.interactions import PostBookmark, PostSubscription
from app.models.user import User
from app.notifications import create_notification

router = APIRouter()


@router.put("/{post_id}/bookmarks/me")
async def bookmark_post(post_id: int, current_user: User = Depends(get_current_active_user)) -> Any:
    ensure_min_trust(
        current_user,
        min_level=TrustLevel.BASIC,
        required_permission="post.bookmark",
    )

    post = await Post.get_or_none(id=post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    _, created = await PostBookmark.get_or_create(user_id=current_user.id, post_id=post_id)
    if created:
        await Post.filter(id=post.id).update(bookmark_count=F("bookmark_count") + 1)
        if post.author_id != current_user.id:
            await create_notification(
                user_id=post.author_id,
                notification_type="post_bookmark",
                title="Your post was bookmarked",
                content=f"{current_user.username} bookmarked your post: {post.title}",
                target_type="post",
                target_id=post.id,
                extra_payload={
                    "space_id": post.space_id,
                    "post_id": post.id,
                },
            )

    return success_response({"bookmarked": True, "created": created})


@router.delete("/{post_id}/bookmarks/me")
async def remove_bookmark(post_id: int, current_user: User = Depends(get_current_active_user)) -> Any:
    ensure_min_trust(
        current_user,
        min_level=TrustLevel.BASIC,
        required_permission="post.bookmark",
    )

    deleted = await PostBookmark.filter(user_id=current_user.id, post_id=post_id).delete()
    if deleted > 0:
        await Post.filter(id=post_id).update(bookmark_count=F("bookmark_count") - 1)
    return success_response({"message": "Bookmark removed"})


@router.put("/{post_id}/likes/me")
async def like_post(post_id: int, current_user: User = Depends(get_current_active_user)) -> Any:
    ensure_min_trust(
        current_user,
        min_level=TrustLevel.BASIC,
        required_permission="post.like",
    )

    post = await Post.get_or_none(id=post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    _, created = await PostLike.get_or_create(user_id=current_user.id, post_id=post_id)
    if created:
        await Post.filter(id=post.id).update(like_count=F("like_count") + 1)
        if post.author_id != current_user.id:
            await create_notification(
                user_id=post.author_id,
                notification_type="post_like",
                title="Your post got a new like",
                content=f"{current_user.username} liked your post: {post.title}",
                target_type="post",
                target_id=post.id,
                extra_payload={
                    "space_id": post.space_id,
                    "post_id": post.id,
                },
            )

    return success_response({"liked": True, "created": created})


@router.delete("/{post_id}/likes/me")
async def unlike_post(post_id: int, current_user: User = Depends(get_current_active_user)) -> Any:
    ensure_min_trust(
        current_user,
        min_level=TrustLevel.BASIC,
        required_permission="post.like",
    )

    deleted = await PostLike.filter(user_id=current_user.id, post_id=post_id).delete()
    if deleted > 0:
        await Post.filter(id=post_id).update(like_count=F("like_count") - 1)
    return success_response({"message": "Like removed"})


@router.put("/{post_id}/subscriptions/me")
async def subscribe_post(post_id: int, current_user: User = Depends(get_current_active_user)) -> Any:
    ensure_min_trust(
        current_user,
        min_level=TrustLevel.BASIC,
        required_permission="post.subscribe",
    )

    post = await Post.get_or_none(id=post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    _, created = await PostSubscription.get_or_create(user_id=current_user.id, post_id=post_id)
    return success_response({"subscribed": True, "created": created})


@router.delete("/{post_id}/subscriptions/me")
async def unsubscribe_post(post_id: int, current_user: User = Depends(get_current_active_user)) -> Any:
    ensure_min_trust(
        current_user,
        min_level=TrustLevel.BASIC,
        required_permission="post.subscribe",
    )

    await PostSubscription.filter(user_id=current_user.id, post_id=post_id).delete()
    return success_response({"message": "Subscription removed"})


async def _verify_post_moderation_scope(user: User, post: Post) -> None:
    await ensure_space_master_or_admin(
        user,
        space_id=post.space_id,
        required_permission="post.moderate",
    )


@router.put("/{post_id}/pin")
async def pin_post(post_id: int, current_user: User = Depends(get_current_active_user)) -> Any:
    post = await Post.get_or_none(id=post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    await _verify_post_moderation_scope(current_user, post)

    post.is_pinned = True
    await post.save()
    return success_response({"message": "Post pinned"})


@router.delete("/{post_id}/pin")
async def unpin_post(post_id: int, current_user: User = Depends(get_current_active_user)) -> Any:
    post = await Post.get_or_none(id=post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    await _verify_post_moderation_scope(current_user, post)

    post.is_pinned = False
    await post.save()
    return success_response({"message": "Post unpinned"})


@router.put("/{post_id}/lock")
async def lock_post(post_id: int, current_user: User = Depends(get_current_active_user)) -> Any:
    post = await Post.get_or_none(id=post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    await _verify_post_moderation_scope(current_user, post)

    post.is_locked = True
    await post.save()
    return success_response({"message": "Post locked"})


@router.delete("/{post_id}/lock")
async def unlock_post(post_id: int, current_user: User = Depends(get_current_active_user)) -> Any:
    post = await Post.get_or_none(id=post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    await _verify_post_moderation_scope(current_user, post)

    post.is_locked = False
    await post.save()
    return success_response({"message": "Post unlocked"})
