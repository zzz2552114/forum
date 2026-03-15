from __future__ import annotations

import asyncio
import re

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status
from jose import JWTError, jwt

from app.core.config import settings
from app.models.user import User
from app.notifications import create_notification
from app.realtime_chat.manager import connection_manager
from app.realtime_chat.schemas import (
    build_chat_event,
    build_history_event,
    build_room_event,
    build_system_event,
)

router = APIRouter()

MAX_CONTENT_LENGTH = 500
LEGACY_ROOM_KEY = "legacy:lobby"
HEARTBEAT_TIMEOUT_SECONDS = 20
MAX_HEARTBEAT_MISSES = 2
HISTORY_REPLAY_LIMIT = 50
MENTION_PATTERN = re.compile(r"@([A-Za-z0-9_]{2,50})")

INVALID_FORMAT_MESSAGE = "消息格式不正确，请发送带 content 字段的 JSON。"


def _clean_username(raw_username: str | None) -> str:
    return (raw_username or "").strip()


def _room_key(space_id: int, section_id: int) -> str:
    return f"{space_id}:{section_id}"


def _parse_last_event_id(raw_value: str | None) -> int:
    if raw_value is None:
        return 0
    try:
        value = int(raw_value)
    except ValueError:
        return 0
    return max(value, 0)


def _extract_message_content(data: dict) -> str:
    content = data.get("content")
    if content is None:
        content = data.get("message")
    return str(content or "").strip()


def _extract_mentions(content: str) -> set[str]:
    return {matched.group(1) for matched in MENTION_PATTERN.finditer(content)}


async def _resolve_sender_user(token: str | None, username: str) -> User | None:
    token = (token or "").strip()
    if not token:
        return None

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        subject = payload.get("sub")
        if subject is None:
            return None
        user_id = int(subject)
    except (JWTError, ValueError, TypeError):
        return None

    user = await User.get_or_none(id=user_id)
    if not user:
        return None

    if user.username != username:
        return None

    return user


async def _notify_chat_mentions(
    *,
    sender: User | None,
    sender_username: str,
    content: str,
    room: str,
    space_id: int,
    section_id: int,
) -> None:
    if not sender:
        return

    mentions = _extract_mentions(content)
    if not mentions:
        return

    if sender.username in mentions:
        mentions.discard(sender.username)

    if not mentions:
        return

    mentioned_users = await User.filter(username__in=list(mentions)).all()
    if not mentioned_users:
        return

    snippet = content[:180]
    for mentioned in mentioned_users:
        if mentioned.id == sender.id:
            continue

        await create_notification(
            user_id=mentioned.id,
            notification_type="chat_mention",
            title="你在即时聊天中被提及了",
            content=f"{sender_username} 在即时聊天中提到了你：{snippet}",
            target_type="space",
            target_id=space_id,
            extra_payload={
                "space_id": space_id,
                "section_id": section_id,
                "room": room,
                "from_username": sender_username,
            },
        )


async def _build_room_event(
    room: str,
    event_type: str,
    message: str,
    *,
    username: str | None = None,
    payload: dict | None = None,
    content: str | None = None,
    record_history: bool = False,
) -> dict:
    event_id = await connection_manager.next_event_id(room)
    online_count = await connection_manager.room_online_count(room)
    event = build_room_event(
        event_id=event_id,
        event_type=event_type,  # type: ignore[arg-type]
        room=room,
        message=message,
        username=username,
        online_count=online_count,
        payload=payload,
        content=content,
    )
    if record_history:
        await connection_manager.record_event(room, event)
    return event


async def _send_room_error(websocket: WebSocket, room: str, message: str) -> None:
    error_event = await _build_room_event(
        room,
        "error",
        message,
        username="system",
        content=message,
        record_history=False,
    )
    await connection_manager.send_personal(websocket, error_event)


@router.websocket("/ws/chat")
async def websocket_chat_legacy(websocket: WebSocket) -> None:
    """Deprecated global room endpoint kept for backward compatibility with the demo."""
    username = _clean_username(websocket.query_params.get("username"))

    if not username:
        await websocket.accept()
        await websocket.close(
            code=status.WS_1008_POLICY_VIOLATION,
            reason="username is required",
        )
        return

    await connection_manager.connect(LEGACY_ROOM_KEY, websocket, username)
    online_count = await connection_manager.room_online_count(LEGACY_ROOM_KEY)
    await connection_manager.broadcast(
        LEGACY_ROOM_KEY,
        build_system_event(f"{username} joined", online_count),
    )

    try:
        while True:
            try:
                data = await websocket.receive_json()
            except WebSocketDisconnect:
                break
            except Exception:
                current_online = await connection_manager.room_online_count(LEGACY_ROOM_KEY)
                await websocket.send_json(
                    build_system_event(INVALID_FORMAT_MESSAGE, current_online)
                )
                continue

            if not isinstance(data, dict):
                current_online = await connection_manager.room_online_count(LEGACY_ROOM_KEY)
                await websocket.send_json(
                    build_system_event(INVALID_FORMAT_MESSAGE, current_online)
                )
                continue

            content = _extract_message_content(data)
            if not content:
                current_online = await connection_manager.room_online_count(LEGACY_ROOM_KEY)
                await websocket.send_json(
                    build_system_event(
                        "消息内容不能为空。",
                        current_online,
                    )
                )
                continue

            if len(content) > MAX_CONTENT_LENGTH:
                current_online = await connection_manager.room_online_count(LEGACY_ROOM_KEY)
                await websocket.send_json(
                    build_system_event(
                        f"消息过长，最多允许 {MAX_CONTENT_LENGTH} 个字符。",
                        current_online,
                    )
                )
                continue

            if not await connection_manager.allow_message(LEGACY_ROOM_KEY, websocket):
                current_online = await connection_manager.room_online_count(LEGACY_ROOM_KEY)
                await websocket.send_json(
                    build_system_event(
                        "发送过于频繁，请稍后再试。",
                        current_online,
                    )
                )
                continue

            await connection_manager.broadcast(
                LEGACY_ROOM_KEY,
                build_chat_event(username, content),
            )
    finally:
        left_user = await connection_manager.disconnect(LEGACY_ROOM_KEY, websocket)
        if left_user:
            current_online = await connection_manager.room_online_count(LEGACY_ROOM_KEY)
            await connection_manager.broadcast(
                LEGACY_ROOM_KEY,
                build_system_event(f"{left_user} left", current_online),
            )


@router.websocket("/ws/chat/{space_id}/{section_id}")
async def websocket_chat_room(websocket: WebSocket, space_id: int, section_id: int) -> None:
    username = _clean_username(websocket.query_params.get("username"))

    if not username:
        await websocket.accept()
        await websocket.close(
            code=status.WS_1008_POLICY_VIOLATION,
            reason="username is required",
        )
        return

    sender = await _resolve_sender_user(websocket.query_params.get("token"), username)
    token_value = (websocket.query_params.get("token") or "").strip()
    if token_value and not sender:
        await websocket.accept()
        await websocket.close(
            code=status.WS_1008_POLICY_VIOLATION,
            reason="invalid token or username mismatch",
        )
        return

    from app.api.deps import ensure_space_subscription
    from fastapi import HTTPException
    
    if not sender:
        await websocket.accept()
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="authentication required")
        return
        
    try:
        await ensure_space_subscription(sender, space_id)
    except HTTPException:
        await websocket.accept()
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="not subscribed to space")
        return

    room = _room_key(space_id, section_id)
    last_event_id = _parse_last_event_id(websocket.query_params.get("last_event_id"))

    await connection_manager.connect(room, websocket, username)

    try:
        history = await connection_manager.history_since(room, last_event_id, HISTORY_REPLAY_LIMIT)
        if history:
            history_event = build_history_event(
                event_id=await connection_manager.next_event_id(room),
                room=room,
                online_count=await connection_manager.room_online_count(room),
                events=history,
                last_event_id=last_event_id,
            )
            await connection_manager.send_personal(websocket, history_event)

        joined_event = await _build_room_event(
            room,
            "presence",
            f"{username} joined",
            username=username,
            content=f"{username} joined",
            record_history=True,
        )
        await connection_manager.broadcast(room, joined_event)

        heartbeat_misses = 0
        while True:
            try:
                data = await asyncio.wait_for(
                    websocket.receive_json(),
                    timeout=HEARTBEAT_TIMEOUT_SECONDS,
                )
            except asyncio.TimeoutError:
                heartbeat_misses += 1
                ping_event = await _build_room_event(
                    room,
                    "presence",
                    "ping",
                    username="system",
                    content="ping",
                    record_history=False,
                )
                await connection_manager.send_personal(websocket, ping_event)
                if heartbeat_misses > MAX_HEARTBEAT_MISSES:
                    break
                continue
            except WebSocketDisconnect:
                break
            except Exception:
                await _send_room_error(websocket, room, INVALID_FORMAT_MESSAGE)
                continue

            heartbeat_misses = 0
            if not isinstance(data, dict):
                await _send_room_error(websocket, room, INVALID_FORMAT_MESSAGE)
                continue

            message_type = str(data.get("type", "")).strip().lower()
            if message_type in {"ping", "pong"}:
                pong_event = await _build_room_event(
                    room,
                    "presence",
                    "pong",
                    username="system",
                    content="pong",
                    record_history=False,
                )
                await connection_manager.send_personal(websocket, pong_event)
                continue

            content = _extract_message_content(data)
            if not content:
                await _send_room_error(websocket, room, "消息内容不能为空。")
                continue

            if len(content) > MAX_CONTENT_LENGTH:
                await _send_room_error(
                    websocket,
                    room,
                    f"消息过长，最多允许 {MAX_CONTENT_LENGTH} 个字符。",
                )
                continue

            if not await connection_manager.allow_message(room, websocket):
                await _send_room_error(websocket, room, "发送过于频繁，请稍后再试。")
                continue

            mentions = sorted(_extract_mentions(content))
            chat_event = await _build_room_event(
                room,
                "chat",
                content,
                username=username,
                content=content,
                payload={"mentions": mentions} if mentions else None,
                record_history=True,
            )
            await connection_manager.broadcast(room, chat_event)

            await _notify_chat_mentions(
                sender=sender,
                sender_username=username,
                content=content,
                room=room,
                space_id=space_id,
                section_id=section_id,
            )
    finally:
        left_user = await connection_manager.disconnect(room, websocket)
        if left_user:
            left_event = await _build_room_event(
                room,
                "presence",
                f"{left_user} left",
                username=left_user,
                content=f"{left_user} left",
                record_history=True,
            )
            await connection_manager.broadcast(room, left_event)
