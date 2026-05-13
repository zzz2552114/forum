from __future__ import annotations

import math
import re
from datetime import datetime
from typing import Callable, Iterable, Literal, Optional

from fastapi import APIRouter, Query
from tortoise.expressions import Q

from app.core.responses import paginate_response, success_response
from app.models.category import Space
from app.models.enums import ContentStatus
from app.models.forum import Post
from app.models.resource import Resource
from app.schemas.common import PaginationData, ResponseBase
from app.schemas.search import (
    AuthorBrief,
    PostSearchItem,
    ResourceSearchItem,
    SearchSuggestions,
    SpaceSearchItem,
)

router = APIRouter()

MAX_PAGE_SIZE = 100
MAX_RANKING_CANDIDATES = 2000
SUGGESTION_LIMIT = 5
TOKEN_SPLIT_RE = re.compile(r"\s+")


def _clamp_page_size(page_size: int) -> int:
    return min(max(page_size, 1), MAX_PAGE_SIZE)


def _resolve_keyword(
    keyword: Optional[str],
    q: Optional[str],
    query: Optional[str],
) -> str:
    value = keyword or q or query or ""
    return value.strip()


def _tokenize_keyword(keyword: str) -> list[str]:
    if not keyword:
        return []
    unique_tokens: list[str] = []
    for token in TOKEN_SPLIT_RE.split(keyword):
        norm = token.strip().casefold()
        if norm and norm not in unique_tokens:
            unique_tokens.append(norm)
    return unique_tokens


def _build_keyword_query(tokens: Iterable[str], fields: tuple[str, ...]) -> Optional[Q]:
    merged: Optional[Q] = None
    for token in tokens:
        token_q: Optional[Q] = None
        for field in fields:
            condition = Q(**{f"{field}__icontains": token})
            token_q = condition if token_q is None else (token_q | condition)
        if token_q is not None:
            merged = token_q if merged is None else (merged | token_q)
    return merged


def _score_match(
    tokens: list[str],
    weighted_texts: list[tuple[int, Optional[str]]],
    keyword_phrase: str,
) -> tuple[bool, float]:
    if not tokens:
        return True, 0.0

    phrase = keyword_phrase.casefold().strip()
    score = 0.0
    matched_tokens = 0

    normalized_texts: list[tuple[int, str]] = []
    for weight, text in weighted_texts:
        if not text:
            continue
        normalized = text.casefold().strip()
        if normalized:
            normalized_texts.append((weight, normalized))

    for token in tokens:
        token_score = 0
        for weight, text in normalized_texts:
            if text == token:
                token_score = max(token_score, 7 * weight)
            elif text.startswith(token):
                token_score = max(token_score, 5 * weight)
            elif token in text:
                token_score = max(token_score, 3 * weight)
        if token_score > 0:
            matched_tokens += 1
            score += token_score

    required_matches = 1 if len(tokens) == 1 else math.ceil(len(tokens) / 2)
    if matched_tokens < required_matches:
        return False, 0.0

    score += (matched_tokens / len(tokens)) * 20

    if phrase:
        for weight, text in normalized_texts:
            if phrase == text:
                score += 16 * weight
                break
            if phrase in text:
                score += 8 * weight
                break

    return True, score


def _sort_ranked_rows(
    rows: Iterable[object],
    tokens: list[str],
    keyword_phrase: str,
    text_builder: Callable[[object], list[tuple[int, Optional[str]]]],
) -> list[object]:
    ranked: list[tuple[float, float, int, object]] = []
    for row in rows:
        passed, score = _score_match(tokens, text_builder(row), keyword_phrase)
        if not passed:
            continue
        created_at = getattr(row, "created_at", None)
        created_at_ts = created_at.timestamp() if isinstance(created_at, datetime) else 0.0
        row_id = int(getattr(row, "id", 0) or 0)
        ranked.append((score, created_at_ts, row_id, row))

    ranked.sort(key=lambda item: (-item[0], -item[1], -item[2]))
    return [item[3] for item in ranked]


def _paginate_rows(rows: list[object], page: int, page_size: int) -> tuple[list[object], int]:
    total = len(rows)
    offset = (page - 1) * page_size
    return rows[offset : offset + page_size], total


# ==========================================
# 全局搜索 - 搜索帖子
# ==========================================
@router.get("/posts", response_model=ResponseBase[PaginationData[PostSearchItem]])
async def search_posts(
    keyword: Optional[str] = Query(default=None, min_length=1),
    q: Optional[str] = Query(default=None, min_length=1),
    query: Optional[str] = Query(default=None, min_length=1),
    space_id: Optional[int] = None,
    post_type: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=MAX_PAGE_SIZE),
):
    page_size = _clamp_page_size(page_size)
    keyword_value = _resolve_keyword(keyword, q, query)
    tokens = _tokenize_keyword(keyword_value)

    post_query = Post.filter(status=ContentStatus.PUBLISHED)
    if tokens:
        keyword_q = _build_keyword_query(tokens, ("title", "content"))
        if keyword_q is not None:
            post_query = post_query.filter(keyword_q)
    if space_id is not None:
        post_query = post_query.filter(space_id=space_id)
    if post_type is not None:
        post_query = post_query.filter(post_type=post_type)

    posts = await (
        post_query.order_by("-created_at")
        .limit(MAX_RANKING_CANDIDATES)
        .prefetch_related("author", "space")
    )

    ranked_posts = _sort_ranked_rows(
        posts,
        tokens,
        keyword_value,
        lambda row: [(12, getattr(row, "title", None)), (2, getattr(row, "content", None))],
    )
    paged_posts, total = _paginate_rows(ranked_posts, page, page_size)

    items: list[PostSearchItem] = []
    for post in paged_posts:
        content = (post.content or "").strip()
        summary = content[:120] + ("..." if len(content) > 120 else "")
        author = getattr(post, "author", None)
        author_payload = (
            AuthorBrief(id=author.id, username=author.username, nickname=author.nickname)
            if author
            else AuthorBrief(id=0, username="unknown")
        )
        space = getattr(post, "space", None)
        items.append(
            PostSearchItem(
                id=post.id,
                title=post.title,
                summary=summary,
                post_type=post.post_type.value if hasattr(post.post_type, "value") else str(post.post_type),
                space_id=post.space_id,
                space_name=space.name if space else "",
                author=author_payload,
                status=post.status.value if hasattr(post.status, "value") else str(post.status),
                is_pinned=post.is_pinned,
                is_featured=post.is_featured,
                view_count=post.view_count,
                like_count=post.like_count,
                comment_count=post.comment_count,
                bookmark_count=post.bookmark_count,
                created_at=post.created_at,
            )
        )

    return paginate_response(items, page, page_size, total)


# ==========================================
# 全局搜索 - 搜索板块
# ==========================================
@router.get("/spaces", response_model=ResponseBase[PaginationData[SpaceSearchItem]])
async def search_spaces(
    keyword: Optional[str] = Query(default=None, min_length=1),
    q: Optional[str] = Query(default=None, min_length=1),
    query: Optional[str] = Query(default=None, min_length=1),
    category_id: Optional[int] = None,
    type: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=MAX_PAGE_SIZE),
):
    page_size = _clamp_page_size(page_size)
    keyword_value = _resolve_keyword(keyword, q, query)
    tokens = _tokenize_keyword(keyword_value)

    space_query = Space.filter(status=ContentStatus.PUBLISHED)
    if tokens:
        keyword_q = _build_keyword_query(tokens, ("name", "description"))
        if keyword_q is not None:
            space_query = space_query.filter(keyword_q)
    if category_id is not None:
        space_query = space_query.filter(category_id=category_id)
    if type is not None:
        space_query = space_query.filter(type=type)

    spaces = await space_query.order_by("-created_at").limit(MAX_RANKING_CANDIDATES)

    ranked_spaces = _sort_ranked_rows(
        spaces,
        tokens,
        keyword_value,
        lambda row: [(7, getattr(row, "name", None)), (3, getattr(row, "description", None))],
    )
    paged_spaces, total = _paginate_rows(ranked_spaces, page, page_size)

    items = [
        SpaceSearchItem(
            id=space.id,
            name=space.name,
            slug=space.slug,
            type=space.type.value if hasattr(space.type, "value") else str(space.type),
            category_id=space.category_id,
            description=space.description,
            post_count=space.post_count,
            resource_count=space.resource_count,
            subscriber_count=space.subscriber_count,
            created_at=space.created_at,
        )
        for space in paged_spaces
    ]

    return paginate_response(items, page, page_size, total)


# ==========================================
# 全局搜索 - 搜索学习资源
# ==========================================
@router.get("/resources", response_model=ResponseBase[PaginationData[ResourceSearchItem]])
async def search_resources(
    keyword: Optional[str] = Query(default=None, min_length=1),
    q: Optional[str] = Query(default=None, min_length=1),
    query: Optional[str] = Query(default=None, min_length=1),
    space_id: Optional[int] = None,
    scope: Optional[Literal["materials", "explore"]] = None,
    school_space_id: Optional[int] = None,
    course_space_id: Optional[int] = None,
    resource_type: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=MAX_PAGE_SIZE),
):
    page_size = _clamp_page_size(page_size)
    keyword_value = _resolve_keyword(keyword, q, query)
    tokens = _tokenize_keyword(keyword_value)

    resource_query = Resource.filter(status=ContentStatus.PUBLISHED)
    if scope == "materials":
        resource_query = resource_query.exclude(resource_type="policy")
    elif scope == "explore":
        resource_query = resource_query.filter(resource_type="policy")

    if space_id is not None:
        resource_query = resource_query.filter(Q(space_id=space_id) | Q(school_space_id=space_id))
    if school_space_id is not None:
        resource_query = resource_query.filter(school_space_id=school_space_id)
    if course_space_id is not None:
        resource_query = resource_query.filter(space_id=course_space_id)
    if resource_type is not None:
        resource_query = resource_query.filter(resource_type=resource_type)

    if tokens:
        keyword_q = _build_keyword_query(
            tokens,
            ("title", "description", "filename", "space__name", "school_space__name"),
        )
        if keyword_q is not None:
            resource_query = resource_query.filter(keyword_q)

    resources = await (
        resource_query.order_by("-created_at")
        .limit(MAX_RANKING_CANDIDATES)
        .prefetch_related("space", "school_space")
    )

    ranked_resources = _sort_ranked_rows(
        resources,
        tokens,
        keyword_value,
        lambda row: [
            (6, getattr(row, "title", None)),
            (5, getattr(row, "filename", None)),
            (3, getattr(row, "description", None)),
            (2, row.space.name if getattr(row, "space", None) else None),
            (2, row.school_space.name if getattr(row, "school_space", None) else None),
        ],
    )
    paged_resources, total = _paginate_rows(ranked_resources, page, page_size)

    items: list[ResourceSearchItem] = []
    for resource in paged_resources:
        course_space = getattr(resource, "space", None)
        school_space = getattr(resource, "school_space", None)
        items.append(
            ResourceSearchItem(
                id=resource.id,
                title=resource.title or resource.filename or "Untitled resource",
                resource_type=resource.resource_type,
                filename=resource.filename or "",
                description=resource.description,
                space_id=resource.space_id,
                space_name=course_space.name if course_space else None,
                school_space_id=resource.school_space_id,
                school_space_name=school_space.name if school_space else None,
                course_space_id=resource.space_id,
                course_space_name=course_space.name if course_space else None,
                download_count=resource.download_count,
                bookmark_count=resource.bookmark_count,
                created_at=resource.created_at,
            )
        )

    return paginate_response(items, page, page_size, total)


# ==========================================
# 搜索建议 (用户输入时自动下拉联想提示)
# ==========================================
@router.get("/suggestions", response_model=ResponseBase[SearchSuggestions])
async def search_suggestions(
    keyword: Optional[str] = Query(default=None, min_length=1),
    q: Optional[str] = Query(default=None, min_length=1),
    query: Optional[str] = Query(default=None, min_length=1),
):
    keyword_value = _resolve_keyword(keyword, q, query)
    tokens = _tokenize_keyword(keyword_value)
    if not tokens:
        return success_response(SearchSuggestions(spaces=[], posts=[], resources=[]))

    space_q = Space.filter(status=ContentStatus.PUBLISHED)
    sq = _build_keyword_query(tokens, ("name",))
    if sq is not None:
        space_q = space_q.filter(sq)
    space_names = await space_q.limit(SUGGESTION_LIMIT).values_list("name", flat=True)

    post_q = Post.filter(status=ContentStatus.PUBLISHED)
    pq = _build_keyword_query(tokens, ("title",))
    if pq is not None:
        post_q = post_q.filter(pq)
    post_titles = await post_q.limit(SUGGESTION_LIMIT).values_list("title", flat=True)

    resource_q = Resource.filter(status=ContentStatus.PUBLISHED)
    rq = _build_keyword_query(tokens, ("title", "filename"))
    if rq is not None:
        resource_q = resource_q.filter(rq)
    resource_titles = await resource_q.limit(SUGGESTION_LIMIT).values_list("title", flat=True)
    resource_names = [item for item in resource_titles if item]

    return success_response(
        SearchSuggestions(
            spaces=list(space_names),
            posts=list(post_titles),
            resources=resource_names,
        )
    )
