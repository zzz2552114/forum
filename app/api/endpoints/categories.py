from fastapi import APIRouter, Depends, HTTPException
from typing import List

from app.api.deps import require_role
from app.core.responses import success_response
from app.models.category import Category
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.category import CategoryCreate, CategoryResponse
from app.schemas.common import ResponseBase

router = APIRouter()


@router.get("/", response_model=ResponseBase[List[CategoryResponse]])
async def read_categories():
    data = await Category.all()
    return success_response(data)


@router.post("/", response_model=ResponseBase[CategoryResponse])
async def create_category(
    category_in: CategoryCreate,
    current_user: User = Depends(
        require_role([UserRole.ADMIN, UserRole.SUPER_ROOT], "category.manage")
    ),
):
    category_exists = await Category.get_or_none(name=category_in.name)
    if category_exists:
        raise HTTPException(status_code=400, detail="Category with this name already exists")
    category = await Category.create(**category_in.model_dump())
    return success_response(category)


@router.get("/{category_id}", response_model=ResponseBase[CategoryResponse])
async def read_category_by_id(category_id: int):
    category = await Category.get_or_none(id=category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return success_response(category)
