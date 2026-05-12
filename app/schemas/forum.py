from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.tag import TagResponse


# --- Post Schemas ---
class PostBase(BaseModel):
    title: str
    content: str
    space_id: int


class PostCreate(BaseModel):
    title: str = Field(..., max_length=255)
    content: str
    space_id: int
    tag_ids: Optional[List[int]] = None
    tag_names: Optional[List[str]] = None


class PostAuthor(BaseModel):
    id: int
    username: str
    nickname: Optional[str] = None
    avatar_url: Optional[str] = None


class PostSpace(BaseModel):
    id: int
    name: str


class PostResponse(PostBase):
    id: int
    author_id: int
    author: Optional[PostAuthor] = None
    space: Optional[PostSpace] = None
    view_count: int
    like_count: int
    comment_count: int
    bookmark_count: int
    created_at: datetime
    updated_at: datetime
    tags: list[TagResponse] = []

    model_config = ConfigDict(from_attributes=True)


class PostContextResponse(BaseModel):
    id: int
    space_id: int


# --- Comment Schemas ---
class CommentBase(BaseModel):
    content: str
    post_id: int
    parent_id: Optional[int] = None


class CommentCreate(CommentBase):
    pass


class CommentAuthorSummary(BaseModel):
    id: int
    username: str
    nickname: Optional[str] = None
    avatar_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class CommentResponse(CommentBase):
    id: int
    author_id: int
    created_at: datetime
    author: Optional[CommentAuthorSummary] = None

    model_config = ConfigDict(from_attributes=True)


class CommentContextResponse(BaseModel):
    id: int
    post_id: int
    parent_id: Optional[int] = None
    space_id: int
