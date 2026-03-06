from fastapi import APIRouter, Depends, HTTPException
from typing import Any

from app.models.user import User
from app.models.enums import SchoolVisibility
from app.schemas.profile import UserProfileResponse, UserProfileBase, UserPrivacyUpdate
from app.api.deps import get_current_active_user
from app.schemas.common import ResponseBase, PaginationData
from app.core.responses import success_response, paginate_response
from app.models.notification import Notification
from app.schemas.notification import NotificationResponse

router = APIRouter()

@router.get("/", response_model=ResponseBase[UserProfileResponse])
async def read_my_profile(
    current_user: User = Depends(get_current_active_user)
) -> Any:
    return success_response(current_user)

@router.patch("/profile", response_model=ResponseBase[UserProfileResponse])
async def update_my_profile(
    profile_in: UserProfileBase,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    update_data = profile_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(current_user, field, value)
        
    await current_user.save()
    return success_response(current_user)

@router.patch("/privacy", response_model=ResponseBase[UserProfileResponse])
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
    return success_response(current_user)

@router.get("/notifications", response_model=ResponseBase[PaginationData[NotificationResponse]])
async def read_my_notifications(
    page: int = 1,
    page_size: int = 20,
    current_user: User = Depends(get_current_active_user)
):
    query = Notification.filter(user_id=current_user.id).order_by("-created_at")
    total = await query.count()
    skip = (page - 1) * page_size
    notifications = await query.offset(skip).limit(page_size)
    
    return paginate_response(notifications, page, page_size, total)

@router.patch("/notifications/{notification_id}/read", response_model=ResponseBase[NotificationResponse])
async def read_notification(
    notification_id: int,
    current_user: User = Depends(get_current_active_user)
):
    notif = await Notification.get_or_none(id=notification_id, user_id=current_user.id)
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")
        
    notif.is_read = True
    await notif.save()
    return success_response(notif)
