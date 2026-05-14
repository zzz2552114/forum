from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import AuthPrincipal, get_optional_principal, is_platform_admin
from app.core.responses import success_response
from app.models.enums import SchoolVisibility
from app.models.user import User
from app.schemas.common import ResponseBase
from app.schemas.profile import UserPublicProfileResponse

router = APIRouter()


# ==========================================
# 获取公开的用户资料 (包含隐私策略控制)
# ==========================================
@router.get("/{user_id}", response_model=ResponseBase[UserPublicProfileResponse])
async def read_user_profile(
    user_id: int,
    principal: AuthPrincipal = Depends(get_optional_principal),
) -> Any:
    user = await User.get_or_none(id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.school_visibility == SchoolVisibility.HIDDEN:
        can_view_hidden = False
        if principal.user is not None:
            if principal.user.id == user.id or is_platform_admin(principal.user):
                can_view_hidden = True

        if not can_view_hidden:
            user.school_name = None

    return success_response(user)
