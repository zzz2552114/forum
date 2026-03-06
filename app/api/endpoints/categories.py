from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.schemas.category import CategoryCreate, CategoryResponse
from app.models.category import Category
from app.api.deps import get_current_active_user
from app.models.user import User

router = APIRouter()

@router.get("/", response_model=List[CategoryResponse])
async def read_categories():
    return await Category.all()

@router.post("/", response_model=CategoryResponse)
async def create_category(category_in: CategoryCreate, current_user: User = Depends(get_current_active_user)):
    # Optional logic: verify if user is admin
    category_exists = await Category.get_or_none(name=category_in.name)
    if category_exists:
        raise HTTPException(status_code=400, detail="Category with this name already exists")
    category = await Category.create(**category_in.model_dump())
    return category

@router.get("/{category_id}", response_model=CategoryResponse)
async def read_category_by_id(category_id: int):
    category = await Category.get_or_none(id=category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category
