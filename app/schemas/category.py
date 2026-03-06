from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, List

# --- Category Schemas ---
class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None

class CategoryCreate(CategoryBase):
    pass

class CategoryResponse(CategoryBase):
    id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

# --- Space Schemas ---
class SpaceBase(BaseModel):
    name: str
    description: Optional[str] = None
    category_id: int

class SpaceCreate(SpaceBase):
    pass

class SpaceResponse(SpaceBase):
    id: int
    owner_id: Optional[int] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
