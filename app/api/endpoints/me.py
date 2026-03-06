from fastapi import APIRouter, Depends, HTTPException
from typing import Any

from app.models.user import User
from app.models.enums import SchoolVisibility
from app.schemas.profile import UserProfileResponse, UserProfileBase, UserPrivacyUpdate
from app.api.deps import get_current_active_user

router = APIRouter()

@router.get("/", response_model=UserProfileResponse)
async def read_my_profile(
    current_user: User = Depends(get_current_active_user)
) -> Any:
    return current_user

@router.patch("/profile", response_model=UserProfileResponse)
async def update_my_profile(
    profile_in: UserProfileBase,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    update_data = profile_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(current_user, field, value)
        
    await current_user.save()
    return current_user

@router.patch("/privacy", response_model=UserProfileResponse)
async def update_my_privacy(
    privacy_in: UserPrivacyUpdate,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    if privacy_in.school_visibility == SchoolVisibility.HIDDEN and current_user.trust_level < 2:
        raise HTTPException(
            status_code=403, 
            detail="Trust level 2 or higher required to hide school"
        )
        
    if privacy_in.school_visibility is not None:
        current_user.school_visibility = privacy_in.school_visibility
        
    await current_user.save()
    return current_user
