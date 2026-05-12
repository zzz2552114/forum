from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


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


class NotificationMarkReadRequest(BaseModel):
    notification_ids: list[int] = Field(default_factory=list)


class NotificationUnreadCountResponse(BaseModel):
    unread_count: int
