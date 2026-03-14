import uuid

from fastapi.testclient import TestClient

from app.models.enums import TrustLevel, UserRole
from main import app
from tests.authz_test_utils import register_and_login

UNIQUE = uuid.uuid4().hex[:8]


def test_post_actions_flow():
    with TestClient(app) as client:
        headers, _, _ = register_and_login(
            client,
            prefix="action_user",
            role=UserRole.ADMIN,
            trust_level=TrustLevel.CONTRIBUTOR,
        )

        # 1. Create a category and space
        cat_resp = client.post(
            "/api/v1/categories/",
            json={
                "name": f"Action Cat {UNIQUE}",
                "description": "For action tests",
            },
            headers=headers,
        )
        assert cat_resp.status_code == 200
        cat_id = cat_resp.json()["data"]["id"]

        space_resp = client.post(
            "/api/v1/spaces/",
            json={
                "name": f"Action Space {UNIQUE}",
                "category_id": cat_id,
            },
            headers=headers,
        )
        assert space_resp.status_code == 200
        space_id = space_resp.json()["data"]["id"]

        # 2. Create a post
        post_resp = client.post(
            "/api/v1/posts/",
            json={
                "title": f"Test Actions {UNIQUE}",
                "content": "Testing likes and bookmarks",
                "space_id": space_id,
            },
            headers=headers,
        )
        assert post_resp.status_code == 200
        post_id = post_resp.json()["data"]["id"]

        # 3. Like the post
        like_resp = client.put(f"/api/v1/posts/{post_id}/likes/me", headers=headers)
        assert like_resp.status_code == 200
        assert like_resp.json()["data"]["liked"] is True

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
        assert bookmark_resp.json()["data"]["bookmarked"] is True

        # Check bookmark count increased
        read_resp3 = client.get(f"/api/v1/posts/{post_id}")
        assert read_resp3.json()["data"]["bookmark_count"] == 1

        # 6. Unbookmark the post
        unbookmark_resp = client.delete(f"/api/v1/posts/{post_id}/bookmarks/me", headers=headers)
        assert unbookmark_resp.status_code == 200

        # Check bookmark count decreased
        read_resp4 = client.get(f"/api/v1/posts/{post_id}")
        assert read_resp4.json()["data"]["bookmark_count"] == 0
