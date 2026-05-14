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
    """
    获取所有分类列表。
    
    允许任何用户（包括未登录游客）获取分类列表。
    返回的结构为标准的统一响应格式。
    """
    # 从数据库中查询所有的分类记录
    data = await Category.all()
    return success_response(data)


@router.post("/", response_model=ResponseBase[CategoryResponse])
async def create_category(
    category_in: CategoryCreate,
    current_user: User = Depends(
        require_role([UserRole.ADMIN, UserRole.SUPER_ROOT], "category.manage")
    ),
):
    """
    创建一个新的分类。
    
    权限要求：必须是 ADMIN 或 SUPER_ROOT 角色。
    参数：
    - category_in: 接收并校验创建分类需要的字段（如分类名称、描述等）
    - current_user: 通过 Depends 注入的当前登录用户，同时在此阶段完成鉴权。
    """
    # 检查数据库中是否已经存在同名分类，避免名称冲突
    category_exists = await Category.get_or_none(name=category_in.name)
    if category_exists:
        raise HTTPException(status_code=400, detail="Category with this name already exists")
        
    # 如果不存在，则使用传入的验证后的参数创建新分类并保存到数据库
    category = await Category.create(**category_in.model_dump())
    return success_response(category)


@router.get("/{category_id}", response_model=ResponseBase[CategoryResponse])
async def read_category_by_id(category_id: int):
    """
    根据分类的 ID 获取单个分类的详细信息。
    
    允许任何用户调用，若找不到则返回 404 错误。
    参数：
    - category_id: 路径参数，指定要查询的分类ID
    """
    # 根据主键 ID 获取单条分类记录，如果没有找到则返回 None
    category = await Category.get_or_none(id=category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
        
    # 找到后返回成功响应
    return success_response(category)
