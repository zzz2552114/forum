import pytest
from fastapi.testclient import TestClient
from main import app
import uuid

UNIQUE = uuid.uuid4().hex[:8]

def _register_and_login(client: TestClient) -> dict:
    username = f"action_user_{UNIQUE}"
    client.post("/api/v1/auth/register", json={
        "username": username,
        "email": f"{username}@test.com",
        "password": "actionpass123"
    })
    login = client.post("/api/v1/auth/login", data={
        "username": username,
        "password": "actionpass123"
    })
    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.mark.asyncio
async def test_post_actions_flow():
    with TestClient(app) as client:
        headers = _register_and_login(client)

        # 1. Create a category and space
        cat_resp = client.post("/api/v1/categories/", json={
            "name": f"Action Cat {UNIQUE}",
            "description": "For action tests"
        }, headers=headers)
        cat_id = cat_resp.json()["data"]["id"]

        space_resp = client.post("/api/v1/spaces/", json={
            "name": f"Action Space {UNIQUE}",
            "category_id": cat_id
        }, headers=headers)
        space_id = space_resp.json()["data"]["id"]

        # 2. Create a post
        post_resp = client.post("/api/v1/posts/", json={
            "title": f"Test Actions {UNIQUE}",
            "content": "Testing likes and bookmarks",
            "space_id": space_id
        }, headers=headers)
        post_id = post_resp.json()["data"]["id"]

        # 3. Like the post
        like_resp = client.put(f"/api/v1/posts/{post_id}/likes/me", headers=headers)
        assert like_resp.status_code == 200
        assert like_resp.json()["data"]["liked"] == True

        # Check like count increased
        read_resp = client.get(f"/api/v1/posts/{post_id}")
        assert read_resp.json()["data"]["like_count"] == 1

        # 4. Unlike the post
        unlike_resp = client.delete(f"/api/v1/posts/{post_id}/likes/me", headers=headers)
        assert unlike_resp.status_code == 200
        
        # Check like count decreased
        read_resp2 = client.get(f"/api/v1/posts/{post_id}")
        assert read_resp2.json()["data"]["like_count"] == 0

        # 5. Bookmark the post
        bookmark_resp = client.put(f"/api/v1/posts/{post_id}/bookmarks/me", headers=headers)
        assert bookmark_resp.status_code == 200
        assert bookmark_resp.json()["data"]["bookmarked"] == True

        # Check bookmark count increased
        read_resp3 = client.get(f"/api/v1/posts/{post_id}")
        assert read_resp3.json()["data"]["bookmark_count"] == 1

        # 6. Unbookmark the post
        unbookmark_resp = client.delete(f"/api/v1/posts/{post_id}/bookmarks/me", headers=headers)
        assert unbookmark_resp.status_code == 200

        # Check bookmark count decreased
        read_resp4 = client.get(f"/api/v1/posts/{post_id}")
        assert read_resp4.json()["data"]["bookmark_count"] == 0
