import pytest
from httpx import AsyncClient, ASGITransport
from main import app
from fastapi.testclient import TestClient

@pytest.mark.asyncio
async def test_categories_and_spaces_flow():
    with TestClient(app) as client:
        import uuid
        unique_suffix = str(uuid.uuid4())[:8]
        username = f"spaceowner_{unique_suffix}"
        
        # 1. Register a test user
        client.post("/api/v1/auth/register", json={
            "username": username,
            "email": f"{username}@example.com",
            "password": "testpassword123"
        })
        
        # 2. Login
        login_response = client.post("/api/v1/auth/login", data={
            "username": username,
            "password": "testpassword123"
        })
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 3. Create Category
        cat_response = client.post("/api/v1/categories/", json={
            "name": f"Test Category {unique_suffix}",
            "description": "A category for testing spaces"
        }, headers=headers)
        assert cat_response.status_code == 200
        category_id = cat_response.json()["data"]["id"]

        # 4. Create Space
        space_response = client.post("/api/v1/spaces/", json={
            "name": f"Test Space {unique_suffix}",
            "description": "A space under the testing category",
            "category_id": category_id
        }, headers=headers)
        assert space_response.status_code == 200
        space_data = space_response.json()["data"]
        assert space_data["name"] == f"Test Space {unique_suffix}"
        assert space_data["category_id"] == category_id
        
        # 5. Read Spaces
        spaces_response = client.get(f"/api/v1/spaces/?category_id={category_id}")
        assert spaces_response.status_code == 200
        assert len(spaces_response.json()["data"]) > 0
