from __future__ import annotations

import re

AI_MENTION_PATTERN = re.compile(r"@ai\b", re.IGNORECASE)


def extract_ai_prompt(text: str | None) -> str | None:
    if not text:
        return None

    matched = AI_MENTION_PATTERN.search(text)
    if not matched:
        return None

    prompt = text[matched.end() :].strip()
    return prompt or None
