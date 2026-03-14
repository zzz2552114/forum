from __future__ import annotations

import asyncio
from collections import deque
from dataclasses import dataclass, field
from time import monotonic
from typing import Any

from fastapi import WebSocket


RATE_LIMIT_WINDOW_SECONDS = 5.0
RATE_LIMIT_MAX_MESSAGES = 8


@dataclass
class RoomState:
    connections: dict[WebSocket, str] = field(default_factory=dict)
    history: deque[dict[str, Any]] = field(default_factory=lambda: deque(maxlen=200))
    next_event_id: int = 0
    send_windows: dict[WebSocket, deque[float]] = field(default_factory=dict)


class ConnectionManager:
    def __init__(self) -> None:
        self._rooms: dict[str, RoomState] = {}
        self._lock = asyncio.Lock()

    def _get_room(self, room: str) -> RoomState:
        state = self._rooms.get(room)
        if not state:
            state = RoomState()
            self._rooms[room] = state
        return state

    async def connect(self, room: str, websocket: WebSocket, username: str) -> None:
        await websocket.accept()
        async with self._lock:
            state = self._get_room(room)
            state.connections[websocket] = username

    async def disconnect(self, room: str, websocket: WebSocket) -> str | None:
        async with self._lock:
            state = self._rooms.get(room)
            if not state:
                return None

            username = state.connections.pop(websocket, None)
            state.send_windows.pop(websocket, None)

            if not state.connections and not state.history:
                self._rooms.pop(room, None)

            return username

    async def room_online_count(self, room: str) -> int:
        async with self._lock:
            state = self._rooms.get(room)
            return len(state.connections) if state else 0

    @property
    def online_count(self) -> int:
        return sum(len(state.connections) for state in self._rooms.values())

    async def next_event_id(self, room: str) -> int:
        async with self._lock:
            state = self._get_room(room)
            state.next_event_id += 1
            return state.next_event_id

    async def record_event(self, room: str, payload: dict[str, Any]) -> None:
        async with self._lock:
            state = self._get_room(room)
            state.history.append(payload)

    async def history_since(self, room: str, last_event_id: int, limit: int = 50) -> list[dict[str, Any]]:
        async with self._lock:
            state = self._rooms.get(room)
            if not state:
                return []

            history = list(state.history)

        if last_event_id <= 0:
            return history[-limit:]

        filtered = [event for event in history if int(event.get("event_id", 0)) > last_event_id]
        return filtered[-limit:]

    async def allow_message(self, room: str, websocket: WebSocket) -> bool:
        now = monotonic()
        async with self._lock:
            state = self._get_room(room)
            window = state.send_windows.setdefault(websocket, deque())
            while window and now - window[0] > RATE_LIMIT_WINDOW_SECONDS:
                window.popleft()

            if len(window) >= RATE_LIMIT_MAX_MESSAGES:
                return False

            window.append(now)
            return True

    async def send_personal(self, websocket: WebSocket, payload: dict[str, Any]) -> None:
        await websocket.send_json(payload)

    async def broadcast(self, room: str, payload: dict[str, Any], exclude: WebSocket | None = None) -> None:
        async with self._lock:
            state = self._rooms.get(room)
            if not state:
                return
            sockets = [socket for socket in state.connections.keys() if socket is not exclude]

        stale_connections: list[WebSocket] = []
        for socket in sockets:
            try:
                await socket.send_json(payload)
            except Exception:
                stale_connections.append(socket)

        if stale_connections:
            async with self._lock:
                state = self._rooms.get(room)
                if not state:
                    return

                for socket in stale_connections:
                    state.connections.pop(socket, None)
                    state.send_windows.pop(socket, None)

    def clear(self) -> None:
        self._rooms.clear()


connection_manager = ConnectionManager()
