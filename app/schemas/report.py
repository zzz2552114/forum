from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.enums import ReviewStatus

class ReportCreate(BaseModel):
    reason: str
    post_id: Optional[int] = None
    comment_id: Optional[int] = None

class ReportUpdate(BaseModel):
    status: ReviewStatus

class ReportResponse(BaseModel):
    id: int
    reporter_id: int
    post_id: Optional[int] = None
    comment_id: Optional[int] = None
    reason: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
