from __future__ import annotations

import asyncio
from dataclasses import dataclass


@dataclass
class AiProviderContext:
    user_id: int
    post_id: int
    space_id: int
    comment_id: int
    post_title: str
    post_content: str
    comment_content: str


class BaseAiProvider:
    async def run(self, prompt: str, context: AiProviderContext) -> str:  # pragma: no cover - interface
        raise NotImplementedError


class MockAiProvider(BaseAiProvider):
    async def run(self, prompt: str, context: AiProviderContext) -> str:
        normalized = prompt.strip()
        if "[fail]" in normalized:
            raise RuntimeError("Mock provider forced failure")
        if "[timeout]" in normalized:
            await asyncio.sleep(10)

        await asyncio.sleep(0.05)
        post_excerpt = context.post_content.strip().replace("\n", " ")[:200]
        return (
            "【AI 回复】\n"
            f"你在帖子《{context.post_title}》下提出的问题是：{normalized}\n"
            f"结合帖子内容，关键信息如下：{post_excerpt}\n"
            "如果你希望我继续展开，可以补充更具体的要求。"
        )