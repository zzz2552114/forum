from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class NotificationResponse(BaseModel):
    id: int
    user_id: int
    type: str
    title: str
    content: str
    is_read: bool
    target_type: Optional[str]
    target_id: Optional[int]
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
