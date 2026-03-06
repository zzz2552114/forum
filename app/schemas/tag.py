from pydantic import BaseModel, ConfigDict
from datetime import datetime

class TagBase(BaseModel):
    name: str
    slug: str | None = None

class TagCreate(TagBase):
    pass

class TagResponse(TagBase):
    id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
