from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from app.schemas.forum import PostCreate, PostResponse
from app.schemas.common import ResponseBase, PaginationData
from app.core.responses import success_response, paginate_response
from app.models.forum import Post, PostLike
from app.models.category import Space
from app.api.deps import get_current_active_user, get_current_user, ensure_space_subscription
from app.models.user import User

router = APIRouter()

from app.models.enums import ContentStatus

# ==========================================
# 分页获取帖子列表 (支持按板块、标签、作者等过滤)
# ==========================================
@router.get("/", response_model=ResponseBase[PaginationData[PostResponse]])
async def read_posts(
    space_id: Optional[int] = None, 
    tag_name: Optional[str] = None,
    author_id: Optional[int] = None,
    bookmarked_by_id: Optional[int] = None,
    page: int = 1, 
    page_size: int = 20
):
    query = Post.filter(status=ContentStatus.PUBLISHED)
    if space_id:
        query = query.filter(space_id=space_id)
    if tag_name:
        query = query.filter(tags__name=tag_name).distinct()
    if author_id:
        query = query.filter(author_id=author_id)
    if bookmarked_by_id:
        query = query.filter(bookmarked_by__user_id=bookmarked_by_id).distinct()
        
    total = await query.count()
    skip = (page - 1) * page_size
    posts = await query.offset(skip).limit(page_size).prefetch_related("author", "space", "tags")
    
    # Map tortoise relational objects to id integers for the response model
    response_posts = []
    for p in posts:
        response_posts.append(PostResponse(
            id=p.id,
            title=p.title,
            content=p.content,
            space_id=p.space.id,
            author_id=p.author.id,
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

# ==========================================
# 获取全站热榜 (按 hot_score 倒序)
# ==========================================
@router.get("/trending", response_model=ResponseBase[PaginationData[PostResponse]])
async def read_trending_posts(page: int = 1, page_size: int = 20):
    query = Post.filter(status=ContentStatus.PUBLISHED).order_by("-hot_score")
    
    total = await query.count()
    skip = (page - 1) * page_size
    posts = await query.offset(skip).limit(page_size).prefetch_related("author", "space", "tags")
    
    response_posts = []
    for p in posts:
        response_posts.append(PostResponse(
            id=p.id,
            title=p.title,
            content=p.content,
            space_id=p.space.id,
            author_id=p.author.id,
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

# ==========================================
# 发布新帖子
# ==========================================
@router.post("/", response_model=ResponseBase[PostResponse])
async def create_post(post_in: PostCreate, current_user: User = Depends(get_current_active_user)):
    space = await Space.get_or_none(id=post_in.space_id)
    if not space:
        raise HTTPException(status_code=404, detail="Space not found")
        
    await ensure_space_subscription(current_user, space.id)
        
    post = await Post.create(
        title=post_in.title,
        content=post_in.content,
        space_id=space.id,
        author_id=current_user.id
    )
    
    from app.models.tag import Tag
    if post_in.tag_ids:
        tags = await Tag.filter(id__in=post_in.tag_ids)
        if tags:
            await post.tags.add(*tags)
    
    if post_in.tag_names:
        new_tags = []
        for name in post_in.tag_names:
            tag, _ = await Tag.get_or_create(name=name)
            new_tags.append(tag)
        if new_tags:
            await post.tags.add(*new_tags)
            
    # Refetch correctly formatted
    await post.fetch_related("author", "space", "tags")
    
    return success_response(PostResponse(
        id=post.id,
        title=post.title,
        content=post.content,
        space_id=post.space_id,
        author_id=post.author_id,
        author={"id": current_user.id, "username": current_user.username, "nickname": current_user.nickname, "avatar_url": current_user.avatar_url},
        space={"id": space.id, "name": space.name},
        view_count=post.view_count,
        like_count=post.like_count,
        comment_count=post.comment_count,
        bookmark_count=post.bookmark_count,
        created_at=post.created_at,
        updated_at=post.updated_at,
        tags=list(post.tags) if hasattr(post, "tags") else []
    ))

# ==========================================
# 获取单个帖子的详细内容 (并增加浏览量)
# ==========================================
@router.get("/{post_id}", response_model=ResponseBase[PostResponse])
async def read_post(post_id: int):
    post = await Post.get_or_none(id=post_id).prefetch_related("author", "space", "tags")
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
        
    from tortoise.expressions import F
    await Post.filter(id=post.id).update(view_count=F("view_count") + 1)
    
    # Reload the post from DB since we updated it directly via queryset
    post = await Post.get(id=post_id).prefetch_related("author", "space", "tags")
    
    return success_response(PostResponse(
        id=post.id,
        title=post.title,
        content=post.content,
        space_id=post.space.id,
        author_id=post.author.id,
        author={"id": post.author.id, "username": post.author.username, "nickname": post.author.nickname, "avatar_url": post.author.avatar_url} if post.author else None,
        space={"id": post.space.id, "name": post.space.name} if post.space else None,
        view_count=post.view_count,
        like_count=post.like_count,
        comment_count=post.comment_count,
        bookmark_count=post.bookmark_count,
        created_at=post.created_at,
        updated_at=post.updated_at,
        tags=list(post.tags) if hasattr(post, "tags") else []
    ))

# ==========================================
# 点赞帖子 (快捷接口，实际调用后端的 post_actions)
# ==========================================
@router.post("/{post_id}/like")
async def like_post(post_id: int, current_user: User = Depends(get_current_active_user)):
    post = await Post.get_or_none(id=post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
        
    like, created = await PostLike.get_or_create(user_id=current_user.id, post_id=post_id)
    if not created:
        raise HTTPException(status_code=400, detail="You have already liked this post")
        
    from tortoise.expressions import F
    await Post.filter(id=post.id).update(like_count=F("like_count") + 1)
    
    return success_response({"message": "Post liked successfully"})

# ==========================================
# 收藏帖子 (快捷接口，实际调用后端的 post_actions)
# ==========================================
@router.post("/{post_id}/bookmark")
async def bookmark_post(post_id: int, current_user: User = Depends(get_current_active_user)):
    from app.models.interactions import PostBookmark
    post = await Post.get_or_none(id=post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
        
    bookmark, created = await PostBookmark.get_or_create(user_id=current_user.id, post_id=post_id)
    if not created:
        # If already bookmarked, let's un-bookmark it (toggle)
        await bookmark.delete()
        from tortoise.expressions import F
        await Post.filter(id=post.id).update(bookmark_count=F("bookmark_count") - 1)
        return success_response({"message": "Post unbookmarked successfully", "bookmarked": False})
        
    from tortoise.expressions import F
    await Post.filter(id=post.id).update(bookmark_count=F("bookmark_count") + 1)
    
    return success_response({"message": "Post bookmarked successfully", "bookmarked": True})
