from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class ReportCreate(BaseModel):
    # 举报内容，必须填
    reason: str
    # 举报的帖子或者评论，二选一
    post_id: Optional[int] = None
    comment_id: Optional[int] = None

class ReportResponse(BaseModel):
    id: int
    reporter_id: int
    reason: str
    status: str
    post_id: Optional[int]
    comment_id: Optional[int]
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
