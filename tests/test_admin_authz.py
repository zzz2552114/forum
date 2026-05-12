import uuid

from fastapi.testclient import TestClient

from app.models.enums import TrustLevel, UserRole
from main import app
from tests.authz_test_utils import register_and_login


def test_admin_management_endpoints():
    with TestClient(app) as client:
        admin_headers, _, _ = register_and_login(
            client,
            prefix="admin_ops",
            role=UserRole.ADMIN,
            trust_level=TrustLevel.CONTRIBUTOR,
        )
        user_headers, _, _ = register_and_login(
            client,
            prefix="normal_user",
            role=UserRole.USER,
            trust_level=TrustLevel.BASIC,
        )

        # Resolve target user id via admin list
        list_users = client.get("/api/v1/admin/users?page=1&page_size=500", headers=admin_headers)
        assert list_users.status_code == 200
        users = list_users.json()["data"]["items"]
        target = next(item for item in users if item["username"].startswith("normal_user_"))
        target_user_id = target["id"]

        # Non-admin cannot access admin users API
        denied = client.get("/api/v1/admin/users", headers=user_headers)
        assert denied.status_code == 403
        assert denied.json()["data"]["required_permission"] == "user.role.manage"

        # Admin can update trust level
        updated_trust = client.patch(
            f"/api/v1/admin/users/{target_user_id}/trust-level",
            json={"trust_level": int(TrustLevel.VERIFIED)},
            headers=admin_headers,
        )
        assert updated_trust.status_code == 200
        assert updated_trust.json()["data"]["trust_level"] == int(TrustLevel.VERIFIED)

        # Admin can update role
        updated_role = client.patch(
            f"/api/v1/admin/users/{target_user_id}/role",
            json={"role": UserRole.USER.value},
            headers=admin_headers,
        )
        assert updated_role.status_code == 200
        assert updated_role.json()["data"]["role"] == UserRole.USER.value

        # Setup a space for space master management
        suffix = uuid.uuid4().hex[:6]
        category = client.post(
            "/api/v1/categories/",
            json={"name": f"Admin Cat {suffix}"},
            headers=admin_headers,
        )
        assert category.status_code == 200
        category_id = category.json()["data"]["id"]

        space = client.post(
            "/api/v1/spaces/",
            json={"name": f"Admin Space {suffix}", "category_id": category_id},
            headers=admin_headers,
        )
        assert space.status_code == 200
        space_id = space.json()["data"]["id"]

        assign_master = client.put(
            f"/api/v1/admin/spaces/{space_id}/masters/{target_user_id}",
            headers=admin_headers,
        )
        assert assign_master.status_code == 200

        masters = client.get(f"/api/v1/admin/spaces/{space_id}/masters", headers=admin_headers)
        assert masters.status_code == 200
        assert any(row["user_id"] == target_user_id for row in masters.json()["data"])

        remove_master = client.delete(
            f"/api/v1/admin/spaces/{space_id}/masters/{target_user_id}",
            headers=admin_headers,
        )
        assert remove_master.status_code == 200
        assert remove_master.json()["data"]["deleted"] is True

