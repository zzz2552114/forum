import uuid

from fastapi.testclient import TestClient

from app.models.enums import TrustLevel, UserRole
from main import app
from tests.authz_test_utils import elevate_user, register_and_login


def test_categories_and_spaces_flow():
    with TestClient(app) as client:
        suffix = uuid.uuid4().hex[:6]
        basic_headers, _, basic_username = register_and_login(
            client,
            prefix="space_basic",
            role=UserRole.USER,
            trust_level=TrustLevel.BASIC,
        )

        # BASIC user cannot create category
        denied_category = client.post(
            "/api/v1/categories/",
            json={"name": f"Denied Category {suffix}", "description": "should fail"},
            headers=basic_headers,
        )
        assert denied_category.status_code == 403
        denied_payload = denied_category.json()
        assert denied_payload["data"]["required_permission"] == "category.manage"

        # BASIC user cannot create space (needs CONTRIBUTOR+)
        denied_space = client.post(
            "/api/v1/spaces/",
            json={"name": f"Denied Space {suffix}", "category_id": 1},
            headers=basic_headers,
        )
        assert denied_space.status_code == 403
        denied_space_payload = denied_space.json()
        assert denied_space_payload["data"]["required_permission"] == "space.create"
        assert denied_space_payload["data"]["required_trust_level"] == int(TrustLevel.CONTRIBUTOR)

        # Promote same account to admin for setup operations
        elevate_user(
            basic_username,
            role=UserRole.ADMIN,
            trust_level=TrustLevel.CONTRIBUTOR,
        )

        # Create Category
        cat_response = client.post(
            "/api/v1/categories/",
            json={
                "name": f"Test Category Elevated {suffix}",
                "description": "A category for testing spaces",
            },
            headers=basic_headers,
        )
        assert cat_response.status_code == 200
        category_id = cat_response.json()["data"]["id"]

        # Create Space
        space_response = client.post(
            "/api/v1/spaces/",
            json={
                "name": f"Test Space Elevated {suffix}",
                "description": "A space under the testing category",
                "category_id": category_id,
            },
            headers=basic_headers,
        )
        assert space_response.status_code == 200
        space_data = space_response.json()["data"]
        assert space_data["name"] == f"Test Space Elevated {suffix}"
        assert space_data["category_id"] == category_id

        # Read Spaces
        spaces_response = client.get(f"/api/v1/spaces/?category_id={category_id}")
        assert spaces_response.status_code == 200
        assert len(spaces_response.json()["data"]) > 0
