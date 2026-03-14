from __future__ import annotations

from typing import Any

from app.models.notification import Notification
from app.notifications.socket import notification_socket_manager


async def create_notification(
    *,
    user_id: int,
    notification_type: str,
    title: str,
    content: str,
    target_type: str | None = None,
    target_id: int | None = None,
    extra_payload: dict[str, Any] | None = None,
) -> Notification:
    notification = await Notification.create(
        user_id=user_id,
        type=notification_type,
        title=title,
        content=content,
        is_read=False,
        target_type=target_type,
        target_id=target_id,
    )

    payload: dict[str, Any] = {
        "type": "notification",
        "notification_id": notification.id,
        "notification_type": notification.type,
        "title": notification.title,
        "content": notification.content,
        "is_read": notification.is_read,
        "target_type": notification.target_type,
        "target_id": notification.target_id,
        "created_at": notification.created_at.isoformat(),
    }
    if extra_payload:
        payload["extra_payload"] = extra_payload
        payload.update(extra_payload)

    await notification_socket_manager.push_to_user(user_id, payload)
    return notification
