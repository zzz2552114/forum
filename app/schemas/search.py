from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime

# --- Search Result Items ---
class AuthorBrief(BaseModel):
    id: int
    username: str
    nickname: Optional[str] = None

class PostSearchItem(BaseModel):
    id: int
    title: str
    summary: str  # truncated content
    post_type: str
    space_id: int
    space_name: str
    author: AuthorBrief
    status: str
    is_pinned: bool = False
    is_featured: bool = False
    view_count: int = 0
    like_count: int = 0
    comment_count: int = 0
    bookmark_count: int = 0
    created_at: datetime

class SpaceSearchItem(BaseModel):
    id: int
    name: str
    slug: Optional[str] = None
    type: str
    category_id: int
    description: Optional[str] = None
    post_count: int = 0
    resource_count: int = 0
    subscriber_count: int = 0
    created_at: datetime

class ResourceSearchItem(BaseModel):
    id: int
    title: Optional[str] = None
    resource_type: Optional[str] = None
    filename: str
    description: Optional[str] = None
    space_id: Optional[int] = None
    space_name: Optional[str] = None
    download_count: int = 0
    bookmark_count: int = 0
    created_at: datetime

# --- Suggestions ---
class SearchSuggestions(BaseModel):
    spaces: List[str] = []
    posts: List[str] = []
    resources: List[str] = []
