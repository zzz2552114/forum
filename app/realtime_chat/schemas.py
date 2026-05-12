from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict

DISPLAY_TIME_FORMAT = "%m-%d %H:%M"
RealtimeRoomEventType = Literal["system", "chat", "history", "error", "presence"]


class LegacyRealtimeChatEvent(BaseModel):
    model_config = ConfigDict(extra="ignore")

    type: Literal["chat", "system"]
    username: str | None = None
    content: str
    timestamp: str
    display_time: str
    online_count: int | None = None


class RealtimeRoomEvent(BaseModel):
    model_config = ConfigDict(extra="ignore")

    event_id: int
    type: RealtimeRoomEventType
    room: str
    message: str
    timestamp: str
    display_time: str
    username: str | None = None
    online_count: int | None = None
    payload: dict[str, Any] | None = None
    # Keep compatibility with existing frontend demo parser expecting `content`.
    content: str | None = None


class RealtimeChatInput(BaseModel):
    model_config = ConfigDict(extra="ignore")

    content: str | None = None
    message: str | None = None
    type: str | None = None


def _now() -> datetime:
    return datetime.now()


def now_timestamp() -> str:
    return _now().isoformat(timespec="seconds")


def now_display_time() -> str:
    return _now().strftime(DISPLAY_TIME_FORMAT)


def build_chat_event(username: str, content: str) -> dict:
    payload = LegacyRealtimeChatEvent(
        type="chat",
        username=username,
        content=content,
        timestamp=now_timestamp(),
        display_time=now_display_time(),
    )
    return payload.model_dump(exclude_none=True)


def build_system_event(content: str, online_count: int) -> dict:
    payload = LegacyRealtimeChatEvent(
        type="system",
        content=content,
        online_count=online_count,
        timestamp=now_timestamp(),
        display_time=now_display_time(),
    )
    return payload.model_dump(exclude_none=True)


def build_room_event(
    *,
    event_id: int,
    event_type: RealtimeRoomEventType,
    room: str,
    message: str,
    username: str | None = None,
    online_count: int | None = None,
    payload: dict[str, Any] | None = None,
    content: str | None = None,
) -> dict[str, Any]:
    event = RealtimeRoomEvent(
        event_id=event_id,
        type=event_type,
        room=room,
        message=message,
        content=content if content is not None else message,
        username=username,
        online_count=online_count,
        payload=payload,
        timestamp=now_timestamp(),
        display_time=now_display_time(),
    )
    return event.model_dump(exclude_none=True)


def build_history_event(
    *,
    event_id: int,
    room: str,
    online_count: int,
    events: list[dict[str, Any]],
    last_event_id: int,
) -> dict[str, Any]:
    replay_count = len(events)
    return build_room_event(
        event_id=event_id,
        event_type="history",
        room=room,
        message=f"Replayed {replay_count} events.",
        online_count=online_count,
        payload={
            "events": events,
            "count": replay_count,
            "last_event_id": last_event_id,
        },
        content=f"Replayed {replay_count} events.",
    )
