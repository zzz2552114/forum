from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.schemas.forum import PostResponse

class MyStatsResponse(BaseModel):
    joined_spaces_count: int
    post_count: int
    resource_count: int
    follower_count: int
    following_count: int
    
    model_config = {
        "from_attributes": True
    }

class MyCommentContextPost(BaseModel):
    id: int
    title: str
    content: str  # We will use this to show a preview snippet
    space_id: int

class MyCommentContextSpace(BaseModel):
    id: int
    name: str

class MyCommentItemResponse(BaseModel):
    id: int
    content: str
    created_at: datetime
    post_id: int
    post: Optional[MyCommentContextPost] = None
    space: Optional[MyCommentContextSpace] = None

    model_config = {
        "from_attributes": True
    }
