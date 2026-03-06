from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime

class ResourceVersionResponse(BaseModel):
    id: int
    file_id: int
    version_note: Optional[str]
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class ResourceBase(BaseModel):
    title: str
    description: Optional[str] = None
    resource_type: Optional[str] = None
    space_id: int

class ResourceCreate(ResourceBase):
    file_id: int
    version_note: Optional[str] = None
    tag_ids: List[int] = []

class ResourceResponse(ResourceBase):
    id: int
    filename: Optional[str]
    uploader_id: int
    download_count: int
    bookmark_count: int
    created_at: datetime
    versions: List[ResourceVersionResponse] = []
    
    model_config = ConfigDict(from_attributes=True)
