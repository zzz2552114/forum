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
    """
    身份上下文数据类
    用于在各个请求中传递当前访问者的核心信息。
    """
    kind: Literal["guest", "user"] # 访问者类型：游客或已登录用户
    user: User | None # 如果是用户，则包含数据库查询出的 User 对象
    role: str # 系统角色（如 guest, user, admin）
    trust_level: TrustLevel # 信任等级


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
        "code": 40301,
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
    """
    【可选鉴权】尝试获取当前用户上下文，不强制要求登录。
    如果请求没有带 Token，会返回游客上下文（guest）；如果带了，则解析用户信息。
    常用于“游客和用户都能看，但用户能看到更多数据”的接口。
    """
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
    """
    【强制鉴权】获取当前登录且账号活跃的用户。
    最常用的依赖：如果你写的接口必须登录才能访问，加上这个 Depends。
    如果没登录，直接拦截并返回 401/403 错误。
    """
    if principal.user is None:
        raise_forbidden(
            required_permission=PERMISSION_AUTH_LOGIN,
            required_trust_level=TrustLevel.BASIC,
            reason="Authentication required",
        )
    return principal.user


def require_role(roles: Sequence[UserRole | str], required_permission: str):
    """
    【角色校验工厂】生成一个要求特定角色的依赖函数。
    用法示例: Depends(require_role([UserRole.ADMIN], "admin.manage"))
    """
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
    """
    【信任等级校验工厂】要求用户的信任等级必须达到 min_level 才能放行。
    用于防止新手灌水（比如 TrustLevel.BASIC 才能发帖）。
    """
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
    """
    【板块订阅检查】确保用户已经订阅（加入）了特定的板块。
    如果是全局管理员或该板块版主，则自动跳过检查。
    """
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
    "report.create",
    "report.manage",
}


async def build_authorization_snapshot(principal: AuthPrincipal) -> dict[str, Any]:
    """
    【生成前端权限快照】
    根据登录用户的 角色、信任等级 以及 担任版主的情况，
    动态计算出该用户拥有哪些细粒度的权限标志（如 `post.create`）。
    这个字典通常返回给前端 Vue，用于控制按钮的显示/隐藏（类似前端鉴权路由/指令）。
    """
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
