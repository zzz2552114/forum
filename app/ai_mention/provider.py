from __future__ import annotations

import asyncio
from dataclasses import dataclass
from openai import AsyncOpenAI
import logging

from app.models.user import User

logger = logging.getLogger(__name__)

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


class DashScopeAiProvider(BaseAiProvider):
    async def run(self, prompt: str, context: AiProviderContext) -> str:
        # Fetch user's ai preferences
        user = await User.get_or_none(id=context.user_id)
        if not user:
            raise ValueError("用户不存在，无法执行 AI 请求")
        
        if not user.ai_api_key:
            raise ValueError("未配置阿里云百炼 API Key，请在个人中心设置。")
            
        model_name = user.ai_model or "qwen-plus"
        api_key = user.ai_api_key
        
        client = AsyncOpenAI(
            api_key=api_key,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
        )
        
        system_prompt = (
            "你是一个论坛的 AI 助手，用户在评论区 @ai 召唤了你。"
            "首先请充分阅读并理解【论坛帖子】标题与内容，掌握整个讨论的背景上下文。"
            "然后，针对用户的具体 prompt 请求，给出一个清晰、专业、合理的回复。"
            "如果用户的需求模糊，请结合帖子主题给出最合适的回答。"
            "回复尽量用 Markdown 格式，且语气要友好。"
        )
        
        post_context = f"帖子标题：《{context.post_title}》\n帖子内容：\n{context.post_content}\n"
        
        # Make the request to dashscope
        try:
            response = await client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"【帖子背景】\n{post_context}\n【用户的提问/要求】\n{prompt}"}
                ],
                temperature=0.7,
                max_tokens=2048
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.exception("AI 调用失败")
            raise RuntimeError(f"调用 Dashscope 错误：{str(e)}")

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