from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.api.deps import (
    ensure_admin_or_super_root,
    get_current_active_user,
    raise_forbidden,
    get_current_user,
)
from app.core.responses import paginate_response, success_response
from app.models.category import Space
from app.models.enums import TrustLevel, UserRole, ReviewStatus
from app.models.interactions import SpaceMaster
from app.models.user import User
from app.models.report import Report
from app.schemas.common import PaginationData, ResponseBase

router = APIRouter()


class UserAdminItem(BaseModel):
    id: int
    username: str
    email: str
    role: UserRole
    trust_level: TrustLevel
    is_active: bool


class UserRoleUpdateRequest(BaseModel):
    role: UserRole


class UserTrustUpdateRequest(BaseModel):
    trust_level: TrustLevel


class SpaceMasterItem(BaseModel):
    user_id: int
    username: str
    assigned_at: Any


# ==========================================
# [管理员] 分页获取全站用户列表
# ==========================================
@router.get("/users", response_model=ResponseBase[PaginationData[UserAdminItem]])
async def list_users(
    page: int = 1,
    page_size: int = 20,
    current_user: User = Depends(get_current_active_user),
):
    ensure_admin_or_super_root(current_user, required_permission="user.role.manage")

    query = User.all().order_by("id")
    total = await query.count()
    skip = (page - 1) * page_size
    users = await query.offset(skip).limit(page_size)

    items = [
        UserAdminItem(
            id=user.id,
            username=user.username,
            email=user.email,
            role=user.role,
            trust_level=user.trust_level,
            is_active=user.is_active,
        )
        for user in users
    ]
    return paginate_response(items, page, page_size, total)


# ==========================================
# [管理员] 修改用户的系统角色 (如设为普通用户或管理员)
# ==========================================
@router.patch("/users/{user_id}/role", response_model=ResponseBase[dict])
async def update_user_role(
    user_id: int,
    payload: UserRoleUpdateRequest,
    current_user: User = Depends(get_current_active_user),
):
    ensure_admin_or_super_root(current_user, required_permission="user.role.manage")

    target = await User.get_or_none(id=user_id)
    if not target:
        raise HTTPException(status_code=404, detail="User not found")

    if target.role == UserRole.SUPER_ROOT and current_user.role != UserRole.SUPER_ROOT:
        raise_forbidden(
            required_permission="user.role.manage",
            reason="Only super_root can modify super_root accounts",
        )

    if payload.role == UserRole.SUPER_ROOT and current_user.role != UserRole.SUPER_ROOT:
        raise_forbidden(
            required_permission="user.role.manage",
            reason="Only super_root can grant super_root role",
        )

    target.role = payload.role
    await target.save(update_fields=["role"])
    return success_response({"id": target.id, "role": target.role})


# ==========================================
# [管理员] 修改用户的信任等级
# ==========================================
@router.patch("/users/{user_id}/trust-level", response_model=ResponseBase[dict])
async def update_user_trust_level(
    user_id: int,
    payload: UserTrustUpdateRequest,
    current_user: User = Depends(get_current_active_user),
):
    ensure_admin_or_super_root(current_user, required_permission="user.trust.manage")

    target = await User.get_or_none(id=user_id)
    if not target:
        raise HTTPException(status_code=404, detail="User not found")

    if target.role == UserRole.SUPER_ROOT and current_user.role != UserRole.SUPER_ROOT:
        raise_forbidden(
            required_permission="user.trust.manage",
            reason="Only super_root can modify super_root accounts",
        )

    target.trust_level = payload.trust_level
    await target.save(update_fields=["trust_level"])
    return success_response({"id": target.id, "trust_level": int(target.trust_level)})


# ==========================================
# [管理员] 获取某个板块的所有版主列表
# ==========================================
@router.get("/spaces/{space_id}/masters", response_model=ResponseBase[list[SpaceMasterItem]])
async def list_space_masters(
    space_id: int,
    current_user: User = Depends(get_current_active_user),
):
    ensure_admin_or_super_root(current_user, required_permission="space.master.manage")

    space = await Space.get_or_none(id=space_id)
    if not space:
        raise HTTPException(status_code=404, detail="Space not found")

    master_rows = await SpaceMaster.filter(space_id=space_id).prefetch_related("user")
    data = [
        SpaceMasterItem(
            user_id=row.user_id,
            username=row.user.username if getattr(row, "user", None) else f"user-{row.user_id}",
            assigned_at=row.assigned_at,
        )
        for row in master_rows
    ]
    return success_response(data)


# ==========================================
# [管理员] 指定某用户成为板块的版主
# ==========================================
@router.put("/spaces/{space_id}/masters/{user_id}", response_model=ResponseBase[dict])
async def assign_space_master(
    space_id: int,
    user_id: int,
    current_user: User = Depends(get_current_active_user),
):
    ensure_admin_or_super_root(current_user, required_permission="space.master.manage")

    space = await Space.get_or_none(id=space_id)
    if not space:
        raise HTTPException(status_code=404, detail="Space not found")

    user = await User.get_or_none(id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    _, created = await SpaceMaster.get_or_create(space_id=space_id, user_id=user_id)
    return success_response({"space_id": space_id, "user_id": user_id, "created": created})


# ==========================================
# [管理员] 撤销某用户的板块版主身份
# ==========================================
@router.delete("/spaces/{space_id}/masters/{user_id}", response_model=ResponseBase[dict])
async def remove_space_master(
    space_id: int,
    user_id: int,
    current_user: User = Depends(get_current_active_user),
):
    ensure_admin_or_super_root(current_user, required_permission="space.master.manage")

    deleted = await SpaceMaster.filter(space_id=space_id, user_id=user_id).delete()
    return success_response({"space_id": space_id, "user_id": user_id, "deleted": bool(deleted)})


