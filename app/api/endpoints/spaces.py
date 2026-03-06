from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.schemas.category import SpaceCreate, SpaceResponse
from app.models.category import Space, Category
from app.api.deps import get_current_active_user
from app.models.user import User

router = APIRouter()

@router.get("/", response_model=List[SpaceResponse])
async def read_spaces(category_id: int | None = None):
    if category_id:
        return await Space.filter(category_id=category_id).all()
    return await Space.all()

@router.post("/", response_model=SpaceResponse)
async def create_space(space_in: SpaceCreate, current_user: User = Depends(get_current_active_user)):
    category = await Category.get_or_none(id=space_in.category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
        
    space_exists = await Space.get_or_none(name=space_in.name, category_id=space_in.category_id)
    if space_exists:
        raise HTTPException(status_code=400, detail="Space with this name already exists in this category")
        
    space = await Space.create(
        **space_in.model_dump(),
        owner=current_user
    )
    return space

@router.get("/{space_id}", response_model=SpaceResponse)
async def read_space_by_id(space_id: int):
    space = await Space.get_or_none(id=space_id)
    if not space:
        raise HTTPException(status_code=404, detail="Space not found")
    # Workaround for asyncmy/tortoise returning owner object or None properly instead of id directly
    await space.fetch_related("owner")
    return SpaceResponse(
        id=space.id,
        name=space.name,
        description=space.description,
        category_id=space.category_id,
        owner_id=space.owner.id if space.owner else None,
        created_at=space.created_at
    )

# --- Space Subscriptions ---
from app.models.interactions import SpaceSubscription

@router.put("/{space_id}/subscriptions/me")
async def subscribe_space(
    space_id: int,
    current_user: User = Depends(get_current_active_user)
):
    space = await Space.get_or_none(id=space_id)
    if not space:
        raise HTTPException(status_code=404, detail="Space not found")
        
    obj, created = await SpaceSubscription.get_or_create(user_id=current_user.id, space_id=space_id)
    if created:
        from tortoise.expressions import F
        await Space.filter(id=space.id).update(subscriber_count=F("subscriber_count") + 1)
    return {"subscribed": True, "created": created}

@router.delete("/{space_id}/subscriptions/me")
async def unsubscribe_space(
    space_id: int,
    current_user: User = Depends(get_current_active_user)
):
    deleted = await SpaceSubscription.filter(user_id=current_user.id, space_id=space_id).delete()
    if deleted > 0:
        from tortoise.expressions import F
        await Space.filter(id=space_id).update(subscriber_count=F("subscriber_count") - 1)
    return {"message": "Subscription removed"}
