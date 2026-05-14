import asyncio
import uuid
from typing import Any

from fastapi.testclient import TestClient

from app.models.enums import TrustLevel, UserRole
from app.models.user import User


def _normalize_trust(value: TrustLevel | int) -> TrustLevel:
    if isinstance(value, TrustLevel):
        return value
    return TrustLevel(int(value))


def _normalize_role(value: UserRole | str) -> UserRole:
    if isinstance(value, UserRole):
        return value
    return UserRole(str(value))


def elevate_user(
    username: str,
    *,
    role: UserRole | str = UserRole.ADMIN,
    trust_level: TrustLevel | int = TrustLevel.CONTRIBUTOR,
) -> None:
    normalized_role = _normalize_role(role)
    normalized_trust = _normalize_trust(trust_level)

    async def _apply() -> None:
        user = await User.get(username=username)
        user.role = normalized_role
        user.trust_level = normalized_trust
        await user.save(update_fields=["role", "trust_level"])

    asyncio.run(_apply())


def register_and_login(
    client: TestClient,
    *,
    prefix: str,
    role: UserRole | str = UserRole.USER,
    trust_level: TrustLevel | int = TrustLevel.BASIC,
) -> tuple[dict[str, str], str, str]:
    suffix = uuid.uuid4().hex[:8]
    username = f"{prefix}_{suffix}"
    password = "testpassword123"

    register = client.post(
        "/api/v1/auth/register",
        json={
            "username": username,
            "email": f"{username}@example.com",
            "password": password,
        },
    )
    assert register.status_code == 200

    normalized_role = _normalize_role(role)
    normalized_trust = _normalize_trust(trust_level)
    if normalized_role != UserRole.USER or normalized_trust != TrustLevel.BASIC:
        elevate_user(username, role=normalized_role, trust_level=normalized_trust)

    login = client.post(
        "/api/v1/auth/login",
        data={"username": username, "password": password},
    )
    assert login.status_code == 200

    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}, token, username


def create_category_and_space(
    client: TestClient,
    headers: dict[str, str],
    *,
    suffix: str,
    category_name: str,
    space_name: str,
) -> tuple[int, int]:
    category = client.post(
        "/api/v1/categories/",
        json={"name": f"{category_name} {suffix}"},
        headers=headers,
    )
    assert category.status_code == 200, f"Expected 200, got {category.status_code}: {category.json()}"
    category_id = category.json()["data"]["id"]

    space = client.post(
        "/api/v1/spaces/",
        json={"name": f"{space_name} {suffix}", "category_id": category_id},
        headers=headers,
    )
    assert space.status_code == 200, f"Expected 200, got {space.status_code}: {space.json()}"
    
    return category_id, space.json()["data"]["id"]
