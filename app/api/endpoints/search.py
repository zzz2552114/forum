from fastapi import APIRouter, Query
from typing import Optional
from tortoise.queryset import Q

from app.models.forum import Post
from app.models.category import Space
from app.models.resource import Resource
from app.models.enums import ContentStatus
from app.schemas.search import (
    PostSearchItem, SpaceSearchItem, ResourceSearchItem,
    AuthorBrief, SearchSuggestions,
)
from app.schemas.common import ResponseBase, PaginationData
from app.core.responses import paginate_response, success_response

router = APIRouter()

MAX_PAGE_SIZE = 100


def _clamp_page_size(page_size: int) -> int:
    return min(max(page_size, 1), MAX_PAGE_SIZE)


# ──────────────────────────────
# 17.1  搜索帖子
# ──────────────────────────────
@router.get("/posts", response_model=ResponseBase[PaginationData[PostSearchItem]])
async def search_posts(
    keyword: str = Query(..., min_length=1, description="搜索关键词"),
    space_id: Optional[int] = None,
    post_type: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=MAX_PAGE_SIZE),
):
    page_size = _clamp_page_size(page_size)
    offset = (page - 1) * page_size

    query = Post.filter(status=ContentStatus.PUBLISHED)
    keywords = [k for k in keyword.split() if k]
    for k in keywords:
        query = query.filter(Q(title__icontains=k) | Q(content__icontains=k))
    if space_id is not None:
        query = query.filter(space_id=space_id)
    if post_type is not None:
        query = query.filter(post_type=post_type)

    total = await query.count()
    posts = await (
        query.order_by("-created_at")
        .offset(offset)
        .limit(page_size)
        .prefetch_related("author", "space")
    )

    items = []
    for p in posts:
        summary = p.content[:120] + ("…" if len(p.content) > 120 else "")
        items.append(
            PostSearchItem(
                id=p.id,
                title=p.title,
                summary=summary,
                post_type=p.post_type.value if hasattr(p.post_type, "value") else str(p.post_type),
                space_id=p.space.id,
                space_name=p.space.name,
                author=AuthorBrief(
                    id=p.author.id,
                    username=p.author.username,
                    nickname=p.author.nickname,
                ),
                status=p.status.value if hasattr(p.status, "value") else str(p.status),
                is_pinned=p.is_pinned,
                is_featured=p.is_featured,
                view_count=p.view_count,
                like_count=p.like_count,
                comment_count=p.comment_count,
                bookmark_count=p.bookmark_count,
                created_at=p.created_at,
            )
        )

    return paginate_response(items, page, page_size, total)


# ──────────────────────────────
# 17.2  搜索空间
# ──────────────────────────────
@router.get("/spaces", response_model=ResponseBase[PaginationData[SpaceSearchItem]])
async def search_spaces(
    keyword: str = Query(..., min_length=1),
    category_id: Optional[int] = None,
    type: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=MAX_PAGE_SIZE),
):
    page_size = _clamp_page_size(page_size)
    offset = (page - 1) * page_size

    query = Space.filter(status=ContentStatus.PUBLISHED)
    keywords = [k for k in keyword.split() if k]
    for k in keywords:
        query = query.filter(Q(name__icontains=k) | Q(description__icontains=k))
    if category_id is not None:
        query = query.filter(category_id=category_id)
    if type is not None:
        query = query.filter(type=type)

    total = await query.count()
    spaces = await query.order_by("-created_at").offset(offset).limit(page_size)

    items = [
        SpaceSearchItem(
            id=s.id,
            name=s.name,
            slug=s.slug,
            type=s.type.value if hasattr(s.type, "value") else str(s.type),
            category_id=s.category_id,
            description=s.description,
            post_count=s.post_count,
            resource_count=s.resource_count,
            subscriber_count=s.subscriber_count,
            created_at=s.created_at,
        )
        for s in spaces
    ]

    return paginate_response(items, page, page_size, total)


# ──────────────────────────────
# 17.3  搜索资料
# ──────────────────────────────
@router.get("/resources", response_model=ResponseBase[PaginationData[ResourceSearchItem]])
async def search_resources(
    keyword: str = Query(..., min_length=1),
    space_id: Optional[int] = None,
    resource_type: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=MAX_PAGE_SIZE),
):
    page_size = _clamp_page_size(page_size)
    offset = (page - 1) * page_size

    query = Resource.filter(status=ContentStatus.PUBLISHED)
    keywords = [k for k in keyword.split() if k]
    for k in keywords:
        query = query.filter(
            Q(title__icontains=k)
            | Q(description__icontains=k)
            | Q(filename__icontains=k)
        )
    if space_id is not None:
        query = query.filter(space_id=space_id)
    if resource_type is not None:
        query = query.filter(resource_type=resource_type)

    total = await query.count()
    resources = await (
        query.order_by("-created_at")
        .offset(offset)
        .limit(page_size)
        .prefetch_related("space")
    )

    items = []
    for r in resources:
        items.append(
            ResourceSearchItem(
                id=r.id,
                title=r.title,
                resource_type=r.resource_type,
                filename=r.filename,
                description=r.description,
                space_id=r.space.id if r.space else None,
                space_name=r.space.name if r.space else None,
                download_count=r.download_count,
                bookmark_count=r.bookmark_count,
                created_at=r.created_at,
            )
        )

    return paginate_response(items, page, page_size, total)


# ──────────────────────────────
# 17.4  搜索联想
# ──────────────────────────────
SUGGESTION_LIMIT = 5


@router.get("/suggestions", response_model=ResponseBase[SearchSuggestions])
async def search_suggestions(
    keyword: str = Query(..., min_length=1),
):
    keywords = [k for k in keyword.split() if k]
    
    sq = Space.filter(status=ContentStatus.PUBLISHED)
    for k in keywords: sq = sq.filter(name__icontains=k)
    space_qs = await sq.limit(SUGGESTION_LIMIT).values_list("name", flat=True)

    pq = Post.filter(status=ContentStatus.PUBLISHED)
    for k in keywords: pq = pq.filter(title__icontains=k)
    post_qs = await pq.limit(SUGGESTION_LIMIT).values_list("title", flat=True)

    rq = Resource.filter(status=ContentStatus.PUBLISHED)
    for k in keywords: rq = rq.filter(Q(title__icontains=k) | Q(filename__icontains=k))
    resource_qs = await rq.limit(SUGGESTION_LIMIT).values_list("title", flat=True)

    # Filter out None entries from resources
    resource_names = [r for r in resource_qs if r]

    return success_response(SearchSuggestions(
        spaces=list(space_qs),
        posts=list(post_qs),
        resources=resource_names,
    ))
