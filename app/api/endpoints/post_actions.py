from fastapi import APIRouter, Depends, HTTPException
from typing import Any

from app.models.user import User
from app.models.forum import Post
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
        
    return {"bookmarked": True, "created": created}

@router.delete("/{post_id}/bookmarks/me")
async def remove_bookmark(
    post_id: int,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    deleted = await PostBookmark.filter(user_id=current_user.id, post_id=post_id).delete()
    if deleted > 0:
        from tortoise.expressions import F
        await Post.filter(id=post_id).update(bookmark_count=F("bookmark_count") - 1)
    return {"message": "Bookmark removed"}

@router.put("/{post_id}/subscriptions/me")
async def subscribe_post(
    post_id: int,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    post = await Post.get_or_none(id=post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
        
    obj, created = await PostSubscription.get_or_create(user_id=current_user.id, post_id=post_id)
    return {"subscribed": True, "created": created}

@router.delete("/{post_id}/subscriptions/me")
async def unsubscribe_post(
    post_id: int,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    await PostSubscription.filter(user_id=current_user.id, post_id=post_id).delete()
    return {"message": "Subscription removed"}

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
    return {"message": "Post pinned"}

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
    return {"message": "Post unpinned"}

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
    return {"message": "Post locked"}

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
    return {"message": "Post unlocked"}
