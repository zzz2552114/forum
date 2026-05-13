from typing import List

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import ensure_min_trust, get_current_active_user
from app.core.responses import success_response
from app.models.category import Category, Space
from app.models.enums import TrustLevel
from app.models.interactions import SpaceSubscription
from app.models.user import User
from app.schemas.category import SpaceCreate, SpaceResponse
from app.schemas.common import ResponseBase

router = APIRouter()


# ==========================================
# 获取所有板块列表 (可按大分类筛选)
# ==========================================
@router.get("/", response_model=ResponseBase[List[SpaceResponse]])
async def read_spaces(category_id: int | None = None):
    if category_id:
        return success_response(await Space.filter(category_id=category_id).all())
    return success_response(await Space.all())


# ==========================================
# 创建新板块
# ==========================================
@router.post("/", response_model=ResponseBase[SpaceResponse])
async def create_space(
    space_in: SpaceCreate,
    current_user: User = Depends(get_current_active_user),
):
    ensure_min_trust(
        current_user,
        min_level=TrustLevel.CONTRIBUTOR,
        required_permission="space.create",
    )

    category = await Category.get_or_none(id=space_in.category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    space_exists = await Space.get_or_none(name=space_in.name, category_id=space_in.category_id)
    if space_exists:
        raise HTTPException(status_code=400, detail="Space with this name already exists in this category")

    space = await Space.create(
        **space_in.model_dump(),
        owner=current_user,
    )
    return success_response(space)


# ==========================================
# 获取单个板块详情
# ==========================================
@router.get("/{space_id}", response_model=ResponseBase[SpaceResponse])
async def read_space_by_id(space_id: int):
    space = await Space.get_or_none(id=space_id)
    if not space:
        raise HTTPException(status_code=404, detail="Space not found")

    await space.fetch_related("owner")
    return success_response(
        SpaceResponse(
            id=space.id,
            name=space.name,
            description=space.description,
            category_id=space.category_id,
            owner_id=space.owner.id if space.owner else None,
            created_at=space.created_at,
        )
    )


# ==========================================
# 加入(订阅)板块
# ==========================================
@router.put("/{space_id}/subscriptions/me")
async def subscribe_space(
    space_id: int,
    current_user: User = Depends(get_current_active_user),
):
    ensure_min_trust(
        current_user,
        min_level=TrustLevel.BASIC,
        required_permission="space.subscribe",
    )

    space = await Space.get_or_none(id=space_id)
    if not space:
        raise HTTPException(status_code=404, detail="Space not found")

    _, created = await SpaceSubscription.get_or_create(user_id=current_user.id, space_id=space_id)
    if created:
        from tortoise.expressions import F

        await Space.filter(id=space.id).update(subscriber_count=F("subscriber_count") + 1)
    return success_response({"subscribed": True, "created": created})


# ==========================================
# 退出(取消订阅)板块
# ==========================================
@router.delete("/{space_id}/subscriptions/me")
async def unsubscribe_space(
    space_id: int,
    current_user: User = Depends(get_current_active_user),
):
    ensure_min_trust(
        current_user,
        min_level=TrustLevel.BASIC,
        required_permission="space.subscribe",
    )

    deleted = await SpaceSubscription.filter(user_id=current_user.id, space_id=space_id).delete()
    if deleted > 0:
        from tortoise.expressions import F

        await Space.filter(id=space_id).update(subscriber_count=F("subscriber_count") - 1)
    return success_response({"message": "Subscription removed"})


# ==========================================
# 获取当前用户加入的所有板块
# ==========================================
@router.get("/me/subscriptions", response_model=ResponseBase[List[SpaceResponse]])
async def get_my_subscriptions(
    current_user: User = Depends(get_current_active_user),
):
    """Get all spaces the current user has subscribed to."""
    subscriptions = await SpaceSubscription.filter(user_id=current_user.id).prefetch_related("space", "space__owner")
    spaces = []
    for sub in subscriptions:
        space = sub.space
        spaces.append(
            SpaceResponse(
                id=space.id,
                name=space.name,
                description=space.description,
                category_id=space.category_id,
                owner_id=space.owner.id if space.owner else None,
                created_at=space.created_at,
            )
        )
    return success_response(spaces)
