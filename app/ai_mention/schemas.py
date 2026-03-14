from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

AiMentionTaskStatus = Literal["queued", "running", "succeeded", "failed", "timeout"]


class AiMentionTaskCreate(BaseModel):
    comment_id: int = Field(gt=0)
    post_id: int = Field(gt=0)
    space_id: int = Field(gt=0)
    prompt: str | None = None
    comment_content: str | None = None


class AiMentionTaskResponse(BaseModel):
    id: str
    user_id: int
    comment_id: int
    post_id: int
    space_id: int
    prompt: str
    status: AiMentionTaskStatus
    result: str | None = None
    error: str | None = None
    retry_count: int
    created_at: datetime
    updated_at: datetime
    finished_at: datetime | None = None
    reply_comment_id: int | None = None

    model_config = ConfigDict(extra="ignore")


class AiTaskNotificationEvent(BaseModel):
    type: Literal["notification"] = "notification"
    notification_id: int
    notification_type: str
    task_id: str
    task_status: AiMentionTaskStatus
    title: str
    content: str
    target_type: str | None = None
    target_id: int | None = None
    created_at: datetime

    model_config = ConfigDict(extra="ignore")
