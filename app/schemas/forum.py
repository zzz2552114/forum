from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

# --- Post Schemas ---
class PostBase(BaseModel):
    title: str
    content: str
    space_id: int

class PostCreate(PostBase):
    pass

class PostResponse(PostBase):
    id: int
    author_id: int
    view_count: int
    like_count: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

# --- Comment Schemas ---
class CommentBase(BaseModel):
    content: str
    post_id: int
    parent_id: Optional[int] = None

class CommentCreate(CommentBase):
    pass

class CommentResponse(CommentBase):
    id: int
    author_id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
