import uuid

from fastapi.testclient import TestClient

from app.models.enums import TrustLevel, UserRole
from main import app
from tests.authz_test_utils import register_and_login


def test_posts_and_comments_flow():
    with TestClient(app) as client:
        suffix = uuid.uuid4().hex[:6]
        admin_headers, _, _ = register_and_login(
            client,
            prefix="forum_admin",
            role=UserRole.ADMIN,
            trust_level=TrustLevel.CONTRIBUTOR,
        )
        user_headers, _, _ = register_and_login(
            client,
            prefix="forum_user",
            role=UserRole.USER,
            trust_level=TrustLevel.BASIC,
        )

        # Setup: admin creates category and space
        cat_response = client.post(
            "/api/v1/categories/",
            json={"name": f"Forum Cat {suffix}"},
            headers=admin_headers,
        )
        assert cat_response.status_code == 200
        category_id = cat_response.json()["data"]["id"]

        space_response = client.post(
            "/api/v1/spaces/",
            json={"name": f"Forum Space {suffix}", "category_id": category_id},
            headers=admin_headers,
        )
        assert space_response.status_code == 200
        space_id = space_response.json()["data"]["id"]

        # BASIC user creates post
        post_response = client.post(
            "/api/v1/posts/",
            json={
                "title": f"Test Title {suffix}",
                "content": "This is the content of the post.",
                "space_id": space_id,
            },
            headers=user_headers,
        )
        assert post_response.status_code == 200
        post_data = post_response.json()["data"]
        post_id = post_data["id"]
        assert post_data["title"] == f"Test Title {suffix}"
        assert post_data["view_count"] == 0
        assert post_data["like_count"] == 0

        # Read Post
        read_post_response = client.get(f"/api/v1/posts/{post_id}")
        assert read_post_response.status_code == 200
        assert read_post_response.json()["data"]["view_count"] == 1

        # Like Post
        like_response = client.post(f"/api/v1/posts/{post_id}/like", headers=user_headers)
        assert like_response.status_code == 200

        # Verify Like Count
        read_post_response2 = client.get(f"/api/v1/posts/{post_id}")
        assert read_post_response2.json()["data"]["like_count"] == 1

        # Create Post 2 for cross-posting tests
        post2_response = client.post(
            "/api/v1/posts/",
            json={
                "title": f"Test Title 2 {suffix}",
                "content": "Another post.",
                "space_id": space_id,
            },
            headers=user_headers,
        )
        assert post2_response.status_code == 200
        post2_id = post2_response.json()["data"]["id"]

        # Create Comment on Post 1
        comment_response = client.post(
            "/api/v1/comments/",
            json={
                "content": "Great post!",
                "post_id": post_id,
            },
            headers=user_headers,
        )
        assert comment_response.status_code == 200
        comment_data = comment_response.json()["data"]
        assert comment_data["content"] == "Great post!"
        comment_id = comment_data["id"]

        # Try to create child comment on Post 2 but parent belongs to Post 1
        bad_comment_response = client.post(
            "/api/v1/comments/",
            json={
                "content": "I agree!",
                "post_id": post2_id,
                "parent_id": comment_id,
            },
            headers=user_headers,
        )
        assert bad_comment_response.status_code == 400
        assert "does not belong" in bad_comment_response.json()["message"]

        # Duplicate like returns 400
        duplicate_like_response = client.post(f"/api/v1/posts/{post_id}/like", headers=user_headers)
        assert duplicate_like_response.status_code == 400

        # Read Comments for Post
        comments_list_response = client.get(f"/api/v1/comments/post/{post_id}")
        assert comments_list_response.status_code == 200
        assert len(comments_list_response.json()["data"]["items"]) > 0
