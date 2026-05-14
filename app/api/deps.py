from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal, Sequence

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from app.core.config import settings
from app.models.enums import TrustLevel, UserRole
from app.models.interactions import SpaceMaster, SpaceSubscription
from app.models.user import User
from app.schemas.token import TokenPayload


oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")
oauth2_optional_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login",
    auto_error=False,
)


PERMISSION_AUTH_LOGIN = "auth.login"


@dataclass(slots=True)
class AuthPrincipal:
    kind: Literal["guest", "user"]
    user: User | None
    role: str
    trust_level: TrustLevel


def _build_credentials_exception() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


def raise_forbidden(
    *,
    required_permission: str | None = None,
    required_trust_level: TrustLevel | None = None,
    reason: str = "Operation not permitted",
) -> None:
    payload: dict[str, Any] = {
        "code": 403,
        "message": "forbidden",
        "data": {
            "reason": reason,
        },
    }
    if required_permission:
        payload["data"]["required_permission"] = required_permission
    if required_trust_level is not None:
        payload["data"]["required_trust_level"] = int(required_trust_level)
    raise HTTPException(status_code=403, detail=payload)


def is_platform_admin(user: User) -> bool:
    return user.role in {UserRole.ADMIN, UserRole.SUPER_ROOT}


async def _decode_user_from_token(token: str) -> User:
    credentials_exception = _build_credentials_exception()
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str | None = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        token_data = TokenPayload(sub=user_id)
    except JWTError as exc:
        raise credentials_exception from exc

    try:
        user_id_int = int(token_data.sub)
    except (ValueError, TypeError) as exc:
        raise credentials_exception from exc

    user = await User.get_or_none(id=user_id_int)
    if user is None:
        raise credentials_exception
    return user


async def get_optional_principal(token: str | None = Depends(oauth2_optional_scheme)) -> AuthPrincipal:
    token_value = (token or "").strip()
    if not token_value:
        return AuthPrincipal(
            kind="guest",
            user=None,
            role="guest",
            trust_level=TrustLevel.GUEST,
        )

    user = await _decode_user_from_token(token_value)
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    return AuthPrincipal(
        kind="user",
        user=user,
        role=user.role,
        trust_level=TrustLevel(int(user.trust_level)),
    )


async def get_principal(token: str = Depends(oauth2_scheme)) -> AuthPrincipal:
    user = await _decode_user_from_token(token)
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    return AuthPrincipal(
        kind="user",
        user=user,
        role=user.role,
        trust_level=TrustLevel(int(user.trust_level)),
    )


async def get_current_user(principal: AuthPrincipal = Depends(get_principal)) -> User:
    if principal.user is None:
        raise _build_credentials_exception()
    return principal.user


async def get_current_active_user(principal: AuthPrincipal = Depends(get_optional_principal)) -> User:
    if principal.user is None:
        raise_forbidden(
            required_permission=PERMISSION_AUTH_LOGIN,
            required_trust_level=TrustLevel.BASIC,
            reason="Authentication required",
        )
    return principal.user


def require_role(roles: Sequence[UserRole | str], required_permission: str):
    role_values = {role.value if isinstance(role, UserRole) else str(role) for role in roles}

    async def role_checker(current_user: User = Depends(get_current_active_user)) -> User:
        if current_user.role not in role_values:
            raise_forbidden(
                required_permission=required_permission,
                reason="Role is not allowed for this operation",
            )
        return current_user

    return role_checker


def ensure_min_trust(user: User, *, min_level: TrustLevel, required_permission: str) -> None:
    if is_platform_admin(user):
        return
    if int(user.trust_level) < int(min_level):
        raise_forbidden(
            required_permission=required_permission,
            required_trust_level=min_level,
            reason="Trust level requirement not met",
        )


def require_min_trust(min_level: TrustLevel, required_permission: str):
    async def trust_checker(current_user: User = Depends(get_current_active_user)) -> User:
        ensure_min_trust(
            current_user,
            min_level=min_level,
            required_permission=required_permission,
        )
        return current_user

    return trust_checker


def ensure_admin_or_super_root(user: User, *, required_permission: str) -> None:
    if is_platform_admin(user):
        return
    raise_forbidden(
        required_permission=required_permission,
        reason="Administrator privileges required",
    )


async def ensure_space_master_or_admin(
    user: User,
    *,
    space_id: int,
    required_permission: str,
) -> None:
    if is_platform_admin(user):
        return

    is_master = await SpaceMaster.filter(user_id=user.id, space_id=space_id).exists()
    if is_master:
        return

    raise_forbidden(
        required_permission=required_permission,
        reason="Space moderator privileges required",
    )


async def ensure_space_subscription(user: User, space_id: int) -> None:
    """Ensure the user has subscribed to the space, or is a space master/admin."""
    if is_platform_admin(user):
        return

    is_sub = await SpaceSubscription.filter(user_id=user.id, space_id=space_id).exists()
    if is_sub:
        return

    is_master = await SpaceMaster.filter(user_id=user.id, space_id=space_id).exists()
    if is_master:
        return

    raise_forbidden(reason="You must join the space to perform this action.")


KNOWN_PERMISSIONS: set[str] = {
    "category.manage",
    "tag.manage",
    "space.create",
    "space.subscribe",
    "space.master.manage",
    "post.create",
    "post.like",
    "post.bookmark",
    "post.subscribe",
    "comment.create",
    "post.moderate",
    "resource.upload",
    "file.upload",
    "file.delete.own",
    "file.delete.any",
    "user.role.manage",
    "user.trust.manage",
    "user.hidden_school.view",
    "report.manage",
}


async def build_authorization_snapshot(principal: AuthPrincipal) -> dict[str, Any]:
    if principal.kind == "guest" or principal.user is None:
        return {
            "auth_state": "guest",
            "role": "guest",
            "trust_level": int(TrustLevel.GUEST),
            "permissions": [],
            "space_permissions": {},
        }

    user = principal.user
    permissions: set[str] = {"file.delete.own"}
    space_permissions: dict[str, list[str]] = {}

    if is_platform_admin(user):
        permissions = set(KNOWN_PERMISSIONS)
        space_permissions["*"] = ["post.moderate", "space.master.manage"]
    else:
        if int(user.trust_level) >= int(TrustLevel.BASIC):
            permissions.update(
                {
                    "post.create",
                    "post.like",
                    "post.bookmark",
                    "post.subscribe",
                    "comment.create",
                    "space.subscribe",
                }
            )
        if int(user.trust_level) >= int(TrustLevel.VERIFIED):
            permissions.update({"resource.upload", "file.upload"})
        if int(user.trust_level) >= int(TrustLevel.CONTRIBUTOR):
            permissions.update({"space.create"})

        space_ids = await SpaceMaster.filter(user_id=user.id).values_list("space_id", flat=True)
        for space_id in space_ids:
            space_permissions[str(space_id)] = ["post.moderate"]

    return {
        "auth_state": "auth",
        "role": user.role,
        "trust_level": int(user.trust_level),
        "permissions": sorted(permissions),
        "space_permissions": space_permissions,
    }
