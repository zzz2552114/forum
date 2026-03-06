from fastapi import APIRouter, Depends, HTTPException
from typing import Any, Optional

from app.models.user import User
from app.models.enums import SchoolVisibility, UserRole
from app.schemas.profile import UserPublicProfileResponse
from app.api.deps import get_current_active_user
from app.schemas.common import ResponseBase
from app.core.responses import success_response

router = APIRouter()

@router.get("/{user_id}", response_model=ResponseBase[UserPublicProfileResponse])
async def read_user_profile(
    user_id: int,
    current_user: Optional[User] = Depends(get_current_active_user)
) -> Any:
    user = await User.get_or_none(id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    # Apply privacy logic
    if user.school_visibility == SchoolVisibility.HIDDEN:
        # Check if viewer is the user themselves or an admin/super_root
        can_view_hidden = False
        if current_user:
            if current_user.id == user.id or current_user.role in [UserRole.ADMIN, UserRole.SUPER_ROOT]:
                can_view_hidden = True
                
        if not can_view_hidden:
            user.school_name = None  # Hide from output
            
    return success_response(user)
