import pytest
from fastapi.testclient import TestClient

from main import app


@pytest.mark.asyncio
async def test_cross_space_and_tags():
    with TestClient(app) as client:
        import uuid

        unique_suffix = str(uuid.uuid4())[:8]
        username = f"user_{unique_suffix}"

        client.post(
            "/api/v1/auth/register",
            json={
                "username": username,
                "email": f"{username}@example.com",
                "password": "testpassword123",
            },
        )
        
        from app.models.user import User
        from app.models.enums import UserRole, TrustLevel
        user = await User.get(username=username)
        user.role = UserRole.ADMIN
        user.trust_level = TrustLevel.CONTRIBUTOR
        await user.save(update_fields=["role", "trust_level"])

        login_response = client.post(
            "/api/v1/auth/login",
            data={
                "username": username,
                "password": "testpassword123",
            },
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        cat_res = client.post("/api/v1/categories/", json={"name": f"School Cat {unique_suffix}"}, headers=headers)
        school_cat_id = cat_res.json()["data"]["id"]

        school_space_res = client.post(
            "/api/v1/spaces/",
            json={"name": f"School {unique_suffix}", "category_id": school_cat_id},
            headers=headers,
        )
        school_space_id = school_space_res.json()["data"]["id"]

        course_space_res = client.post(
            "/api/v1/spaces/",
            json={"name": f"Course {unique_suffix}", "category_id": school_cat_id},
            headers=headers,
        )
        course_space_id = course_space_res.json()["data"]["id"]

        file_res = client.post(
            "/api/v1/files/",
            files={"file": ("test.pdf", b"dummy content", "application/pdf")},
            data={"biz_type": "resource"},
            headers=headers,
        )
        file_id = file_res.json()["data"]["id"]

        res_response = client.post(
            "/api/v1/resources/",
            json={
                "title": "Dual Space Resource",
                "description": "Test dual",
                "space_id": course_space_id,
                "school_space_id": school_space_id,
                "resource_type": "policy",
                "file_id": file_id,
            },
            headers=headers,
        )
        assert res_response.status_code == 200

        course_res_list = client.get(f"/api/v1/resources/?space_id={course_space_id}&resource_type=policy")
        assert len(course_res_list.json()["data"]["items"]) == 1

        school_res_list = client.get(f"/api/v1/resources/?space_id={school_space_id}&resource_type=policy")
        assert len(school_res_list.json()["data"]["items"]) == 1

        post_response = client.post(
            "/api/v1/posts/",
            json={
                "title": "Trade Post",
                "content": "Selling books",
                "space_id": school_space_id,
                "tag_names": ["交易"],
            },
            headers=headers,
        )
        assert post_response.status_code == 200

        tagged_posts = client.get("/api/v1/posts/?tag_name=交易")
        assert len(tagged_posts.json()["data"]["items"]) >= 1
        assert any(p["title"] == "Trade Post" for p in tagged_posts.json()["data"]["items"])

        client.post(
            "/api/v1/posts/",
            json={
                "title": "Normal Post",
                "content": "Not selling",
                "space_id": school_space_id,
            },
            headers=headers,
        )

        tagged_posts_after = client.get("/api/v1/posts/?tag_name=交易")
        trade_items = tagged_posts_after.json()["data"]["items"]
        assert not any(p["title"] == "Normal Post" for p in trade_items)
