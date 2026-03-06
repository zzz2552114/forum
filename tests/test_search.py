import pytest
import uuid
from fastapi.testclient import TestClient
from main import app

UNIQUE = uuid.uuid4().hex[:8]

def _register_and_login(client: TestClient) -> dict:
    """Helper: register a fresh user and return auth headers."""
    username = f"search_user_{UNIQUE}"
    client.post("/api/v1/auth/register", json={
        "username": username,
        "email": f"{username}@test.com",
        "password": "searchpass123"
    })
    login = client.post("/api/v1/auth/login", data={
        "username": username,
        "password": "searchpass123"
    })
    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_search_full_flow():
    with TestClient(app) as client:
        headers = _register_and_login(client)

        # 1. Create a category and space
        cat = client.post("/api/v1/categories/", json={
            "name": f"Search Cat {UNIQUE}",
            "description": "For search tests"
        }, headers=headers)
        cat_id = cat.json()["data"]["id"]

        space = client.post("/api/v1/spaces/", json={
            "name": f"高等数学_{UNIQUE}",
            "category_id": cat_id
        }, headers=headers)
        space_id = space.json()["data"]["id"]

        # 2. Create posts with distinguishable titles
        client.post("/api/v1/posts/", json={
            "title": f"高数期末怎么复习_{UNIQUE}",
            "content": "请问一下大佬们期末怎么复习高数啊",
            "space_id": space_id
        }, headers=headers)

        client.post("/api/v1/posts/", json={
            "title": f"线性代数心得_{UNIQUE}",
            "content": "线性代数课程总结",
            "space_id": space_id
        }, headers=headers)

        # --- 17.1  搜索帖子 ---
        # Search by keyword that matches first post only
        r = client.get(f"/api/v1/search/posts?keyword=高数")
        assert r.status_code == 200
        body = r.json()["data"]
        assert "items" in body
        assert "pagination" in body
        assert body["pagination"]["total"] >= 1
        titles = [item["title"] for item in body["items"]]
        assert any("高数" in t for t in titles)

        # Search with space_id filter
        r2 = client.get(f"/api/v1/search/posts?keyword=高数&space_id={space_id}")
        assert r2.status_code == 200
        assert r2.json()["data"]["pagination"]["total"] >= 1

        # Search with keyword that won't match anything
        r3 = client.get("/api/v1/search/posts?keyword=zzzznotfound999")
        assert r3.status_code == 200
        assert r3.json()["data"]["pagination"]["total"] == 0

        # --- 17.2  搜索空间 ---
        r4 = client.get(f"/api/v1/search/spaces?keyword=高等数学")
        assert r4.status_code == 200
        assert r4.json()["data"]["pagination"]["total"] >= 1
        assert any("高等数学" in s["name"] for s in r4.json()["data"]["items"])

        # --- 17.3  搜索资料 (empty but should work) ---
        r5 = client.get("/api/v1/search/resources?keyword=不存在的资料")
        assert r5.status_code == 200
        assert r5.json()["data"]["pagination"]["total"] == 0

        # --- 17.4  搜索联想 ---
        r6 = client.get(f"/api/v1/search/suggestions?keyword=高")
        assert r6.status_code == 200
        sugg = r6.json()["data"]
        assert "spaces" in sugg
        assert "posts" in sugg
        assert "resources" in sugg
        # Should have at least one suggestion from either spaces or posts
        assert len(sugg["spaces"]) + len(sugg["posts"]) >= 1

        # --- Pagination sanity check ---
        r7 = client.get(f"/api/v1/search/posts?keyword=高数&page=1&page_size=1")
        assert r7.status_code == 200
        pg = r7.json()["data"]["pagination"]
        assert pg["page"] == 1
        assert pg["page_size"] == 1
