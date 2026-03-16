from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Literal
from uuid import uuid4

from tortoise.expressions import F

from app.ai_mention.parser import extract_ai_prompt
from app.ai_mention.provider import AiProviderContext, BaseAiProvider, MockAiProvider, DashScopeAiProvider
from app.ai_mention.schemas import AiMentionTaskCreate, AiMentionTaskResponse
from app.core.security import get_password_hash
from app.models.forum import Comment, Post
from app.models.user import User
from app.notifications import create_notification

AiTaskStatus = Literal["queued", "running", "succeeded", "failed", "timeout"]

DEFAULT_WORKERS = 2
DEFAULT_TIMEOUT_SECONDS = 120
DEFAULT_MAX_RETRIES = 1
AI_BOT_USERNAME = "ai_assistant"
AI_BOT_EMAIL = "ai_assistant@forum.local"


@dataclass
class AiTaskRecord:
    id: str
    user_id: int
    comment_id: int
    post_id: int
    space_id: int
    prompt: str
    comment_content: str
    post_title: str
    post_content: str
    status: AiTaskStatus
    retry_count: int
    created_at: datetime
    updated_at: datetime
    finished_at: datetime | None = None
    result: str | None = None
    error: str | None = None
    reply_comment_id: int | None = None

    def to_response(self) -> AiMentionTaskResponse:
        return AiMentionTaskResponse(
            id=self.id,
            user_id=self.user_id,
            comment_id=self.comment_id,
            post_id=self.post_id,
            space_id=self.space_id,
            prompt=self.prompt,
            status=self.status,
            retry_count=self.retry_count,
            created_at=self.created_at,
            updated_at=self.updated_at,
            finished_at=self.finished_at,
            result=self.result,
            error=self.error,
            reply_comment_id=self.reply_comment_id,
        )


class AiMentionService:
    def __init__(
        self,
        provider: BaseAiProvider | None = None,
        workers: int = DEFAULT_WORKERS,
        timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
        max_retries: int = DEFAULT_MAX_RETRIES,
    ) -> None:
        self._provider = provider or DashScopeAiProvider()
        self._workers = workers
        self._timeout_seconds = timeout_seconds
        self._max_retries = max_retries

        self._queue: asyncio.Queue[str] = asyncio.Queue()
        self._queue_loop: asyncio.AbstractEventLoop | None = None
        self._lock = asyncio.Lock()
        self._worker_tasks: list[asyncio.Task] = []

        self._tasks: dict[str, AiTaskRecord] = {}
        self._task_ids_by_user: dict[int, list[str]] = {}
        self._idempotency_index: dict[tuple[int, int], str] = {}

    async def ensure_started(self) -> None:
        current_loop = asyncio.get_running_loop()
        async with self._lock:
            # TestClient may create different event loops between tests.
            # Recreate queue/workers when loop context changes.
            if self._queue_loop is not current_loop:
                for worker in self._worker_tasks:
                    if not worker.done():
                        worker.cancel()
                self._worker_tasks = []
                self._queue = asyncio.Queue()
                self._queue_loop = current_loop

            active_workers = [task for task in self._worker_tasks if not task.done()]
            if active_workers:
                self._worker_tasks = active_workers
                return

            self._worker_tasks = [
                asyncio.create_task(self._worker_loop(worker_id))
                for worker_id in range(self._workers)
            ]

    def _resolve_prompt(self, payload: AiMentionTaskCreate) -> str:
        direct_prompt = (payload.prompt or "").strip()
        if direct_prompt:
            return direct_prompt

        parsed = extract_ai_prompt(payload.comment_content)
        if parsed:
            return parsed

        raise ValueError("未找到有效的 @ai 提问内容")

    async def create_task(
        self,
        user_id: int,
        payload: AiMentionTaskCreate,
    ) -> tuple[AiTaskRecord, bool]:
        await self.ensure_started()

        prompt = self._resolve_prompt(payload)

        comment = await Comment.get_or_none(id=payload.comment_id)
        if not comment:
            raise ValueError("评论不存在")
        if comment.post_id != payload.post_id:
            raise ValueError("评论不属于当前帖子")
        if comment.author_id != user_id:
            raise ValueError("只有评论作者可以触发 @ai")
        if comment.parent_id is not None:
            raise ValueError("@ai 仅支持在一级评论中使用")

        post = await Post.get_or_none(id=payload.post_id)
        if not post:
            raise ValueError("帖子不存在")
        if post.space_id != payload.space_id:
            raise ValueError("帖子不属于当前空间")

        idempotency_key = (user_id, payload.comment_id)

        async with self._lock:
            existing_task_id = self._idempotency_index.get(idempotency_key)
            if existing_task_id:
                existing = self._tasks[existing_task_id]
                return existing, False

            now = datetime.now(UTC)
            task_id = uuid4().hex
            task = AiTaskRecord(
                id=task_id,
                user_id=user_id,
                comment_id=payload.comment_id,
                post_id=payload.post_id,
                space_id=payload.space_id,
                prompt=prompt,
                comment_content=(payload.comment_content or comment.content or "").strip(),
                post_title=post.title,
                post_content=post.content,
                status="queued",
                retry_count=0,
                created_at=now,
                updated_at=now,
            )
            self._tasks[task_id] = task
            self._idempotency_index[idempotency_key] = task_id
            self._task_ids_by_user.setdefault(user_id, []).append(task_id)

        await self._queue.put(task_id)
        return task, True

    async def get_task_for_user(self, user_id: int, task_id: str) -> AiTaskRecord | None:
        async with self._lock:
            task = self._tasks.get(task_id)
            if not task or task.user_id != user_id:
                return None
            return task

    async def list_tasks_for_user(self, user_id: int) -> list[AiTaskRecord]:
        async with self._lock:
            task_ids = list(self._task_ids_by_user.get(user_id, []))
            tasks = [self._tasks[task_id] for task_id in task_ids]

        return sorted(tasks, key=lambda item: item.created_at, reverse=True)

    async def _worker_loop(self, worker_id: int) -> None:
        while True:
            task_id = await self._queue.get()
            try:
                await self._process_task(task_id)
            finally:
                self._queue.task_done()

    async def _process_task(self, task_id: str) -> None:
        async with self._lock:
            task = self._tasks.get(task_id)
            if not task:
                return
            task.status = "running"
            task.updated_at = datetime.now(UTC)

        success = False
        timeout = False
        result_text: str | None = None
        error_text: str | None = None

        for attempt in range(self._max_retries + 1):
            try:
                context = AiProviderContext(
                    user_id=task.user_id,
                    comment_id=task.comment_id,
                    post_id=task.post_id,
                    space_id=task.space_id,
                    post_title=task.post_title,
                    post_content=task.post_content,
                    comment_content=task.comment_content,
                )
                result_text = await asyncio.wait_for(
                    self._provider.run(task.prompt, context),
                    timeout=self._timeout_seconds,
                )
                success = True
                error_text = None
                break
            except asyncio.TimeoutError:
                timeout = True
                error_text = "AI 任务处理超时"
            except Exception as exc:
                error_text = str(exc)

            async with self._lock:
                latest = self._tasks.get(task_id)
                if latest:
                    latest.retry_count = attempt + 1
                    latest.updated_at = datetime.now(UTC)

        reply_comment_id: int | None = None
        if success and result_text:
            reply_comment_id = await self._create_ai_reply_comment(task, result_text)

        async with self._lock:
            latest = self._tasks.get(task_id)
            if not latest:
                return

            latest.result = result_text
            latest.error = None if success else error_text
            latest.status = "succeeded" if success else ("timeout" if timeout else "failed")
            latest.finished_at = datetime.now(UTC)
            latest.updated_at = latest.finished_at
            latest.reply_comment_id = reply_comment_id

            task_snapshot = AiTaskRecord(
                id=latest.id,
                user_id=latest.user_id,
                comment_id=latest.comment_id,
                post_id=latest.post_id,
                space_id=latest.space_id,
                prompt=latest.prompt,
                comment_content=latest.comment_content,
                post_title=latest.post_title,
                post_content=latest.post_content,
                status=latest.status,
                retry_count=latest.retry_count,
                created_at=latest.created_at,
                updated_at=latest.updated_at,
                finished_at=latest.finished_at,
                result=latest.result,
                error=latest.error,
                reply_comment_id=latest.reply_comment_id,
            )

        await self._emit_notification(task_snapshot)

    async def _ensure_ai_bot_user(self) -> User:
        user = await User.get_or_none(username=AI_BOT_USERNAME)
        if user:
            return user

        user = await User.create(
            username=AI_BOT_USERNAME,
            email=AI_BOT_EMAIL,
            hashed_password=get_password_hash(uuid4().hex),
            nickname="AI 助手",
            bio="论坛 AI 助手",
            is_active=True,
        )
        return user

    async def _create_ai_reply_comment(self, task: AiTaskRecord, result_text: str) -> int:
        ai_user = await self._ensure_ai_bot_user()

        reply = await Comment.create(
            content=result_text,
            post_id=task.post_id,
            parent_id=task.comment_id,
            author_id=ai_user.id,
        )

        await Comment.filter(id=task.comment_id).update(reply_count=F("reply_count") + 1)
        await Post.filter(id=task.post_id).update(
            comment_count=F("comment_count") + 1,
            updated_at=datetime.now(UTC),
        )
        return reply.id

    async def _emit_notification(self, task: AiTaskRecord) -> None:
        if task.status == "succeeded":
            title = "AI 回复已生成"
            content = (task.result or "AI 已完成你的提问。")[:300]
        elif task.status == "timeout":
            title = "AI 回复超时"
            content = "AI 没有在预期时间内完成回复，请稍后再试。"
        else:
            title = "AI 回复失败"
            content = task.error or "AI 执行失败，请稍后重试。"

        await create_notification(
            user_id=task.user_id,
            notification_type="ai_reply",
            title=title,
            content=content,
            target_type="comment",
            target_id=task.reply_comment_id or task.comment_id,
            extra_payload={
                "space_id": task.space_id,
                "post_id": task.post_id,
                "comment_id": task.comment_id,
                "task_id": task.id,
                "task_status": task.status,
                "reply_comment_id": task.reply_comment_id,
            },
        )

    async def reset_for_tests(self) -> None:
        worker_tasks = list(self._worker_tasks)
        self._worker_tasks = []

        for task in worker_tasks:
            if not task.done():
                task.cancel()

        async with self._lock:
            self._tasks.clear()
            self._task_ids_by_user.clear()
            self._idempotency_index.clear()

        while not self._queue.empty():
            try:
                self._queue.get_nowait()
                self._queue.task_done()
            except asyncio.QueueEmpty:
                break

        self._queue = asyncio.Queue()
        self._queue_loop = asyncio.get_running_loop()

        # Swap provider to MockAiProvider for test isolation
        self._provider = MockAiProvider()
        self._timeout_seconds = DEFAULT_TIMEOUT_SECONDS


ai_mention_service = AiMentionService()