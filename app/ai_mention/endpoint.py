from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, status
from jose import JWTError, jwt

from app.ai_mention.notification_socket import notification_socket_manager
from app.ai_mention.schemas import AiMentionTaskCreate, AiMentionTaskResponse
from app.ai_mention.service import ai_mention_service
from app.api.deps import get_current_active_user
from app.core.config import settings
from app.core.responses import paginate_response, success_response
from app.models.user import User
from app.schemas.common import PaginationData, ResponseBase

router = APIRouter()
websocket_router = APIRouter()


def _decode_ws_user_id(token: str) -> int:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        sub = payload.get("sub")
        if sub is None:
            raise ValueError("Missing token subject")
        return int(sub)
    except (JWTError, ValueError, TypeError) as exc:
        raise ValueError("Invalid token") from exc


@router.post("/tasks", response_model=ResponseBase[AiMentionTaskResponse])
async def create_ai_mention_task(
    payload: AiMentionTaskCreate,
    current_user: User = Depends(get_current_active_user),
):
    try:
        task, created = await ai_mention_service.create_task(current_user.id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    message = "task queued" if created else "task already exists"
    return success_response(task.to_response(), message=message)


@router.get("/tasks/my", response_model=ResponseBase[PaginationData[AiMentionTaskResponse]])
async def list_my_ai_mention_tasks(
    page: int = 1,
    page_size: int = 20,
    current_user: User = Depends(get_current_active_user),
):
    tasks = await ai_mention_service.list_tasks_for_user(current_user.id)
    total = len(tasks)

    offset = max(page - 1, 0) * page_size
    sliced = tasks[offset : offset + page_size]
    serialized = [task.to_response() for task in sliced]

    return paginate_response(serialized, page, page_size, total)


@router.get("/tasks/{task_id}", response_model=ResponseBase[AiMentionTaskResponse])
async def get_ai_mention_task(
    task_id: str,
    current_user: User = Depends(get_current_active_user),
):
    task = await ai_mention_service.get_task_for_user(current_user.id, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return success_response(task.to_response())


@websocket_router.websocket("/ws/notifications")
async def websocket_notifications(websocket: WebSocket) -> None:
    token = (websocket.query_params.get("token") or "").strip()
    if not token:
        await websocket.accept()
        await websocket.close(
            code=status.WS_1008_POLICY_VIOLATION,
            reason="token is required",
        )
        return

    try:
        user_id = _decode_ws_user_id(token)
    except ValueError:
        await websocket.accept()
        await websocket.close(
            code=status.WS_1008_POLICY_VIOLATION,
            reason="invalid token",
        )
        return

    await notification_socket_manager.connect(user_id, websocket)

    try:
        while True:
            text = await websocket.receive_text()
            if text.strip().lower() == "ping":
                await websocket.send_json({"type": "pong"})
    except WebSocketDisconnect:
        pass
    finally:
        await notification_socket_manager.disconnect(user_id, websocket)
