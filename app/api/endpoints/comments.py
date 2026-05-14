from __future__ import annotations

import re
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException
from tortoise.expressions import F

from app.ai_mention.parser import extract_ai_prompt
from app.ai_mention.schemas import AiMentionTaskCreate
from app.ai_mention.service import ai_mention_service
from app.api.deps import ensure_min_trust, get_current_active_user
from app.core.responses import paginate_response, success_response
from app.models.enums import ContentStatus, TrustLevel
from app.models.forum import Comment, Post
from app.models.user import User
from app.notifications import create_notification
from app.schemas.common import PaginationData, ResponseBase
from app.schemas.forum import CommentAuthorSummary, CommentContextResponse, CommentCreate, CommentResponse

router = APIRouter()

AI_MENTION_REGEX = re.compile(r"@ai\b", re.IGNORECASE)
NESTED_AI_MENTION_ERROR = "@ai is only supported in top-level comments"
EMPTY_AI_PROMPT_ERROR = "Please include a prompt after @ai"
COMMENT_REPLY_TITLE = "Your comment has a new reply"
POST_COMMENT_TITLE = "Your post has a new comment"


def _serialize_comment(comment: Comment) -> CommentResponse:
    author = getattr(comment, "author", None)
    author_payload = None
    if author:
        author_payload = CommentAuthorSummary(
            id=author.id,
            username=author.username,
            nickname=author.nickname,
            avatar_url=author.avatar_url,
        )

    return CommentResponse(
        id=comment.id,
        content=comment.content,
        post_id=comment.post_id,
        parent_id=comment.parent_id,
        author_id=comment.author_id,
        created_at=comment.created_at,
        author=author_payload,
    )


# ==========================================
# 分页获取某个帖子下的所有评论
# ==========================================
@router.get("/post/{post_id}", response_model=ResponseBase[PaginationData[CommentResponse]])
async def read_comments_for_post(post_id: int, page: int = 1, page_size: int = 50):
    post = await Post.get_or_none(id=post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    query = Comment.filter(post_id=post_id, status=ContentStatus.PUBLISHED).order_by("created_at")
    total = await query.count()
    skip = (page - 1) * page_size
    comments = await query.offset(skip).limit(page_size).prefetch_related("author", "parent")

    response_comments = [_serialize_comment(comment) for comment in comments]
    return paginate_response(response_comments, page, page_size, total)


# ==========================================
# 获取某条评论的上下文信息（所属帖子和板块）
# ==========================================
@router.get("/{comment_id}/context", response_model=ResponseBase[CommentContextResponse])
async def read_comment_context(comment_id: int):
    comment = await Comment.get_or_none(id=comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    post = await Post.get_or_none(id=comment.post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    return success_response(
        CommentContextResponse(
            id=comment.id,
            post_id=comment.post_id,
            parent_id=comment.parent_id,
            space_id=post.space_id,
        )
    )


# ==========================================
# 发布新评论 (支持@AI及回复他人评论)
# ==========================================
@router.post("/", response_model=ResponseBase[CommentResponse])
async def create_comment(comment_in: CommentCreate, current_user: User = Depends(get_current_active_user)):
    ensure_min_trust(
        current_user,
        min_level=TrustLevel.BASIC,
        required_permission="comment.create",
    )

    post = await Post.get_or_none(id=comment_in.post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    from app.api.deps import ensure_space_subscription
    await ensure_space_subscription(current_user, post.space_id)

    parent: Comment | None = None
    if comment_in.parent_id:
        parent = await Comment.get_or_none(id=comment_in.parent_id)
        if not parent:
            raise HTTPException(status_code=404, detail="Parent comment not found")
        if parent.post_id != post.id:
            raise HTTPException(status_code=400, detail="Parent comment does not belong to this post")

    ai_prompt: str | None = None
    has_ai_mention = bool(AI_MENTION_REGEX.search(comment_in.content))

    if parent and has_ai_mention:
        raise HTTPException(status_code=400, detail=NESTED_AI_MENTION_ERROR)

    if not parent and has_ai_mention:
        ai_prompt = extract_ai_prompt(comment_in.content)
        if not ai_prompt:
            raise HTTPException(status_code=400, detail=EMPTY_AI_PROMPT_ERROR)

    comment = await Comment.create(
        content=comment_in.content,
        post_id=post.id,
        parent_id=comment_in.parent_id,
        author_id=current_user.id,
    )
    await comment.fetch_related("author")

    await Post.filter(id=post.id).update(
        updated_at=datetime.now(UTC),
        comment_count=F("comment_count") + 1,
    )

    if parent:
        await Comment.filter(id=parent.id).update(reply_count=F("reply_count") + 1)

    if parent and parent.author_id != current_user.id:
        await create_notification(
            user_id=parent.author_id,
            notification_type="comment_reply",
            title=COMMENT_REPLY_TITLE,
            content=comment_in.content[:180],
            target_type="comment",
            target_id=comment.id,
            extra_payload={
                "space_id": post.space_id,
                "post_id": post.id,
                "comment_id": comment.id,
                "parent_comment_id": parent.id,
            },
        )

    if not parent and post.author_id != current_user.id:
        await create_notification(
            user_id=post.author_id,
            notification_type="comment_reply",
            title=POST_COMMENT_TITLE,
            content=comment_in.content[:180],
            target_type="comment",
            target_id=comment.id,
            extra_payload={
                "space_id": post.space_id,
                "post_id": post.id,
                "comment_id": comment.id,
            },
        )

    if ai_prompt:
        await ai_mention_service.create_task(
            current_user.id,
            AiMentionTaskCreate(
                comment_id=comment.id,
                post_id=post.id,
                space_id=post.space_id,
                prompt=ai_prompt,
                comment_content=comment_in.content,
            ),
        )

    return success_response(_serialize_comment(comment))
