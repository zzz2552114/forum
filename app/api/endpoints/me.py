from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import (
    AuthPrincipal,
    build_authorization_snapshot,
    ensure_min_trust,
    get_current_active_user,
    get_optional_principal,
)
from app.core.responses import paginate_response, success_response
from app.models.enums import SchoolVisibility, TrustLevel
from app.models.notification import Notification
from app.models.user import User
from app.schemas.common import PaginationData, ResponseBase
from app.schemas.notification import (
    NotificationMarkReadRequest,
    NotificationResponse,
    NotificationUnreadCountResponse,
)
from app.schemas.profile import UserPrivacyUpdate, UserProfileBase, UserProfileResponse

router = APIRouter()


@router.get("/", response_model=ResponseBase[UserProfileResponse])
async def read_my_profile(current_user: User = Depends(get_current_active_user)) -> Any:
    return success_response(current_user)


@router.get("/authorization", response_model=ResponseBase[dict])
async def read_my_authorization(principal: AuthPrincipal = Depends(get_optional_principal)) -> Any:
    snapshot = await build_authorization_snapshot(principal)
    return success_response(snapshot)


@router.patch("/profile", response_model=ResponseBase[UserProfileResponse])
async def update_my_profile(
    profile_in: UserProfileBase,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    update_data = profile_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(current_user, field, value)

    await current_user.save()
    return success_response(current_user)


@router.patch("/privacy", response_model=ResponseBase[UserProfileResponse])
async def update_my_privacy(
    privacy_in: UserPrivacyUpdate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    if privacy_in.school_visibility == SchoolVisibility.HIDDEN:
        ensure_min_trust(
            current_user,
            min_level=TrustLevel.VERIFIED,
            required_permission="user.hidden_school.view",
        )

    if privacy_in.school_visibility is not None:
        current_user.school_visibility = privacy_in.school_visibility

    await current_user.save()
    return success_response(current_user)


@router.get("/notifications", response_model=ResponseBase[PaginationData[NotificationResponse]])
async def read_my_notifications(
    page: int = 1,
    page_size: int = 20,
    current_user: User = Depends(get_current_active_user),
):
    query = Notification.filter(user_id=current_user.id).order_by("-created_at")
    total = await query.count()
    skip = (page - 1) * page_size
    notifications = await query.offset(skip).limit(page_size)

    return paginate_response(notifications, page, page_size, total)


@router.get("/notifications/unread-count", response_model=ResponseBase[NotificationUnreadCountResponse])
async def read_unread_notification_count(current_user: User = Depends(get_current_active_user)):
    unread_count = await Notification.filter(user_id=current_user.id, is_read=False).count()
    return success_response(NotificationUnreadCountResponse(unread_count=unread_count))


@router.patch("/notifications/{notification_id}/read", response_model=ResponseBase[NotificationResponse])
async def read_notification(
    notification_id: int,
    current_user: User = Depends(get_current_active_user),
):
    notif = await Notification.get_or_none(id=notification_id, user_id=current_user.id)
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")

    notif.is_read = True
    await notif.save(update_fields=["is_read"])
    return success_response(notif)


@router.patch("/notifications/read", response_model=ResponseBase[dict])
async def mark_notifications_as_read(
    payload: NotificationMarkReadRequest,
    current_user: User = Depends(get_current_active_user),
):
    query = Notification.filter(user_id=current_user.id, is_read=False)
    if payload.notification_ids:
        query = query.filter(id__in=payload.notification_ids)

    updated = await query.update(is_read=True)
    return success_response({"updated": updated})


@router.post("/notifications/read", response_model=ResponseBase[dict])
async def mark_notifications_as_read_legacy(
    payload: NotificationMarkReadRequest,
    current_user: User = Depends(get_current_active_user),
):
    return await mark_notifications_as_read(payload, current_user)
