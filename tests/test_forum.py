import pytest
from httpx import AsyncClient, ASGITransport
from main import app
from fastapi.testclient import TestClient

@pytest.mark.asyncio
async def test_posts_and_comments_flow():
    with TestClient(app) as client:
        import uuid
        unique_suffix = str(uuid.uuid4())[:8]
        username = f"postauthor_{unique_suffix}"
        
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
        
        # Setup: Create Category and Space to put the post in
        cat_response = client.post("/api/v1/categories/", json={"name": f"Cat {unique_suffix}"}, headers=headers)
        category_id = cat_response.json()["data"]["id"]
        
        space_response = client.post("/api/v1/spaces/", json={"name": f"Space {unique_suffix}", "category_id": category_id}, headers=headers)
        space_id = space_response.json()["data"]["id"]

        # 3. Create Post
        post_response = client.post("/api/v1/posts/", json={
            "title": f"Test Title {unique_suffix}",
            "content": "This is the content of the post.",
            "space_id": space_id
        }, headers=headers)
        assert post_response.status_code == 200
        post_data = post_response.json()["data"]
        post_id = post_data["id"]
        assert post_data["title"] == f"Test Title {unique_suffix}"
        assert post_data["view_count"] == 0
        assert post_data["like_count"] == 0
        
        # 4. Read Post
        read_post_response = client.get(f"/api/v1/posts/{post_id}")
        assert read_post_response.status_code == 200
        assert read_post_response.json()["data"]["view_count"] == 1
        
        # 5. Like Post
        like_response = client.post(f"/api/v1/posts/{post_id}/like", headers=headers)
        assert like_response.status_code == 200
        
        # Verify Like Count
        read_post_response2 = client.get(f"/api/v1/posts/{post_id}")
        assert read_post_response2.json()["data"]["like_count"] == 1
        
        # 6. Create Post 2 for cross-posting tests
        post2_response = client.post("/api/v1/posts/", json={
            "title": f"Test Title 2 {unique_suffix}",
            "content": "Another post.",
            "space_id": space_id
        }, headers=headers)
        post2_id = post2_response.json()["data"]["id"]

        # 7. Create Comment on Post 1
        comment_response = client.post("/api/v1/comments/", json={
            "content": "Great post!",
            "post_id": post_id
        }, headers=headers)
        assert comment_response.status_code == 200
        comment_data = comment_response.json()["data"]
        assert comment_data["content"] == "Great post!"
        comment_id = comment_data["id"]
        
        # 8. Try to create child comment on Post 2 but parent belongs to Post 1
        bad_comment_response = client.post("/api/v1/comments/", json={
            "content": "I agree!",
            "post_id": post2_id,
            "parent_id": comment_id
        }, headers=headers)
        assert bad_comment_response.status_code == 400
        assert "does not belong" in bad_comment_response.json()["message"]
        
        # 9. Test duplicate like returns 400
        duplicate_like_response = client.post(f"/api/v1/posts/{post_id}/like", headers=headers)
        assert duplicate_like_response.status_code == 400
        
        # 10. Read Comments for Post
        comments_list_response = client.get(f"/api/v1/comments/post/{post_id}")
        assert comments_list_response.status_code == 200
        assert len(comments_list_response.json()["data"]["items"]) > 0
