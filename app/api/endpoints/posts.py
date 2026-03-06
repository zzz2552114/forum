from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from app.schemas.forum import PostCreate, PostResponse
from app.models.forum import Post, PostLike
from app.models.category import Space
from app.api.deps import get_current_active_user, get_current_user
from app.models.user import User

router = APIRouter()

@router.get("/", response_model=List[PostResponse])
async def read_posts(space_id: Optional[int] = None, skip: int = 0, limit: int = 20):
    query = Post.all()
    if space_id:
        query = query.filter(space_id=space_id)
    posts = await query.offset(skip).limit(limit).prefetch_related("author", "space")
    
    # Map tortoise relational objects to id integers for the response model
    response_posts = []
    for p in posts:
        response_posts.append(PostResponse(
            id=p.id,
            title=p.title,
            content=p.content,
            space_id=p.space.id,
            author_id=p.author.id,
            view_count=p.view_count,
            like_count=p.like_count,
            created_at=p.created_at,
            updated_at=p.updated_at
        ))
    return response_posts

@router.post("/", response_model=PostResponse)
async def create_post(post_in: PostCreate, current_user: User = Depends(get_current_active_user)):
    space = await Space.get_or_none(id=post_in.space_id)
    if not space:
        raise HTTPException(status_code=404, detail="Space not found")
        
    post = await Post.create(
        title=post_in.title,
        content=post_in.content,
        space_id=space.id,
        author_id=current_user.id
    )
    
    return PostResponse(
        id=post.id,
        title=post.title,
        content=post.content,
        space_id=post.space_id,
        author_id=post.author_id,
        view_count=post.view_count,
        like_count=post.like_count,
        created_at=post.created_at,
        updated_at=post.updated_at
    )

@router.get("/{post_id}", response_model=PostResponse)
async def read_post(post_id: int):
    post = await Post.get_or_none(id=post_id).prefetch_related("author", "space")
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
        
    from tortoise.expressions import F
    await Post.filter(id=post.id).update(view_count=F("view_count") + 1)
    
    # Reload the post from DB since we updated it directly via queryset
    post = await Post.get(id=post_id).prefetch_related("author", "space")
    
    return PostResponse(
        id=post.id,
        title=post.title,
        content=post.content,
        space_id=post.space.id,
        author_id=post.author.id,
        view_count=post.view_count,
        like_count=post.like_count,
        created_at=post.created_at,
        updated_at=post.updated_at
    )

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
    
    return {"message": "Post liked successfully"}
