from fastapi import APIRouter, Depends, HTTPException
from typing import Any

from app.models.user import User
from app.models.forum import Post, PostLike
from app.core.responses import success_response
from app.models.enums import UserRole
from app.models.interactions import PostBookmark, PostSubscription
from app.api.deps import get_current_active_user

router = APIRouter()

# --- User Actions ---
@router.put("/{post_id}/bookmarks/me")
async def bookmark_post(
    post_id: int,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    post = await Post.get_or_none(id=post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
        
    obj, created = await PostBookmark.get_or_create(user_id=current_user.id, post_id=post_id)
    if created:
        from tortoise.expressions import F
        await Post.filter(id=post.id).update(bookmark_count=F("bookmark_count") + 1)
        
    return success_response({"bookmarked": True, "created": created})

@router.delete("/{post_id}/bookmarks/me")
async def remove_bookmark(
    post_id: int,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    deleted = await PostBookmark.filter(user_id=current_user.id, post_id=post_id).delete()
    if deleted > 0:
        from tortoise.expressions import F
        await Post.filter(id=post_id).update(bookmark_count=F("bookmark_count") - 1)
    return success_response({"message": "Bookmark removed"})

@router.put("/{post_id}/likes/me")
async def like_post(
    post_id: int,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    post = await Post.get_or_none(id=post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
        
    obj, created = await PostLike.get_or_create(user_id=current_user.id, post_id=post_id)
    if created:
        from tortoise.expressions import F
        # Use existing 'view_count' or default property syntax if 'like_count' doesn't exist,
        # but the prompt implies it exists. We'll update like_count.
        await Post.filter(id=post.id).update(like_count=F("like_count") + 1)
        
    return success_response({"liked": True, "created": created})

@router.delete("/{post_id}/likes/me")
async def unlike_post(
    post_id: int,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    deleted = await PostLike.filter(user_id=current_user.id, post_id=post_id).delete()
    if deleted > 0:
        from tortoise.expressions import F
        await Post.filter(id=post_id).update(like_count=F("like_count") - 1)
    return success_response({"message": "Like removed"})

@router.put("/{post_id}/subscriptions/me")
async def subscribe_post(
    post_id: int,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    post = await Post.get_or_none(id=post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
        
    obj, created = await PostSubscription.get_or_create(user_id=current_user.id, post_id=post_id)
    return success_response({"subscribed": True, "created": created})

@router.delete("/{post_id}/subscriptions/me")
async def unsubscribe_post(
    post_id: int,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    await PostSubscription.filter(user_id=current_user.id, post_id=post_id).delete()
    return success_response({"message": "Subscription removed"})

# --- Mod Actions ---
def _verify_mod(user: User):
    if user.role not in [UserRole.SUPER_ROOT, UserRole.ADMIN, UserRole.MASTER]:
        raise HTTPException(status_code=403, detail="Moderator privileges required")

@router.put("/{post_id}/pin")
async def pin_post(
    post_id: int,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    _verify_mod(current_user)
    post = await Post.get_or_none(id=post_id)
    if not post: raise HTTPException(status_code=404, detail="Post not found")
    post.is_pinned = True
    await post.save()
    return success_response({"message": "Post pinned"})

@router.delete("/{post_id}/pin")
async def unpin_post(
    post_id: int,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    _verify_mod(current_user)
    post = await Post.get_or_none(id=post_id)
    if not post: raise HTTPException(status_code=404, detail="Post not found")
    post.is_pinned = False
    await post.save()
    return success_response({"message": "Post unpinned"})

@router.put("/{post_id}/lock")
async def lock_post(
    post_id: int,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    _verify_mod(current_user)
    post = await Post.get_or_none(id=post_id)
    if not post: raise HTTPException(status_code=404, detail="Post not found")
    post.is_locked = True
    await post.save()
    return success_response({"message": "Post locked"})

@router.delete("/{post_id}/lock")
async def unlock_post(
    post_id: int,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    _verify_mod(current_user)
    post = await Post.get_or_none(id=post_id)
    if not post: raise HTTPException(status_code=404, detail="Post not found")
    post.is_locked = False
    await post.save()
    return success_response({"message": "Post unlocked"})
