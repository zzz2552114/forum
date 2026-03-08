from fastapi import APIRouter, Depends, HTTPException
from typing import List
from datetime import datetime, UTC
from app.schemas.forum import CommentCreate, CommentResponse
from app.schemas.common import ResponseBase, PaginationData
from app.core.responses import success_response, paginate_response
from app.models.forum import Comment, Post
from app.api.deps import get_current_active_user
from app.models.user import User

router = APIRouter()

from app.models.enums import ContentStatus

@router.get("/post/{post_id}", response_model=ResponseBase[PaginationData[CommentResponse]])
async def read_comments_for_post(post_id: int, page: int = 1, page_size: int = 50):
    post = await Post.get_or_none(id=post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
        
    query = Comment.filter(post_id=post_id, status=ContentStatus.PUBLISHED)
    total = await query.count()
    skip = (page - 1) * page_size
    comments = await query.offset(skip).limit(page_size).prefetch_related("author", "parent")
    
    response_comments = []
    for c in comments:
        response_comments.append(CommentResponse(
            id=c.id,
            content=c.content,
            post_id=post_id,
            parent_id=c.parent.id if c.parent else None,
            author_id=c.author.id,
            created_at=c.created_at
        ))
    return paginate_response(response_comments, page, page_size, total)

@router.post("/", response_model=ResponseBase[CommentResponse])
async def create_comment(comment_in: CommentCreate, current_user: User = Depends(get_current_active_user)):
    post = await Post.get_or_none(id=comment_in.post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
        
    if comment_in.parent_id:
        parent = await Comment.get_or_none(id=comment_in.parent_id)
        if not parent:
            raise HTTPException(status_code=404, detail="Parent comment not found")
        if parent.post_id != post.id:
            raise HTTPException(status_code=400, detail="Parent comment does not belong to this post")
            
    comment = await Comment.create(
        content=comment_in.content,
        post_id=post.id,
        parent_id=comment_in.parent_id,
        author_id=current_user.id
    )
    
    post.updated_at = datetime.now(UTC)
    await post.save(update_fields=["updated_at"])
    
    return success_response(CommentResponse(
        id=comment.id,
        content=comment.content,
        post_id=comment.post_id,
        parent_id=comment.parent_id,
        author_id=comment.author_id,
        created_at=comment.created_at
    ))
