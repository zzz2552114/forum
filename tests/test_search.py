import io
import uuid

from fastapi.testclient import TestClient

from main import app
from tests.authz_test_utils import elevate_user


UNIQUE = uuid.uuid4().hex[:8]


def _register_and_login(client: TestClient) -> dict[str, str]:
    username = f"search_user_{UNIQUE}"
    password = "searchpass123"
    register = client.post(
        "/api/v1/auth/register",
        json={
            "username": username,
            "email": f"{username}@test.com",
            "password": password,
        },
    )
    assert register.status_code == 200

    from app.models.enums import TrustLevel, UserRole

    elevate_user(username, role=UserRole.ADMIN, trust_level=TrustLevel.CONTRIBUTOR)

    login = client.post(
        "/api/v1/auth/login",
        data={"username": username, "password": password},
    )
    assert login.status_code == 200
    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def _create_category(client: TestClient, headers: dict[str, str], name: str) -> int:
    resp = client.post(
        "/api/v1/categories/",
        json={"name": f"{name}_{UNIQUE}", "description": "search test category"},
        headers=headers,
    )
    assert resp.status_code == 200
    return resp.json()["data"]["id"]


def _create_space(client: TestClient, headers: dict[str, str], name: str, category_id: int) -> int:
    resp = client.post(
        "/api/v1/spaces/",
        json={"name": f"{name}_{UNIQUE}", "category_id": category_id},
        headers=headers,
    )
    assert resp.status_code == 200
    return resp.json()["data"]["id"]


def _subscribe_space(client: TestClient, headers: dict[str, str], space_id: int) -> None:
    resp = client.put(f"/api/v1/spaces/{space_id}/subscriptions/me", headers=headers)
    assert resp.status_code == 200


def _create_post(
    client: TestClient,
    headers: dict[str, str],
    *,
    title: str,
    content: str,
    space_id: int,
) -> int:
    resp = client.post(
        "/api/v1/posts/",
        json={"title": f"{title}_{UNIQUE}", "content": content, "space_id": space_id},
        headers=headers,
    )
    assert resp.status_code == 200
    return resp.json()["data"]["id"]


def _upload_file(client: TestClient, headers: dict[str, str], filename: str) -> int:
    payload = io.BytesIO(b"search test file")
    resp = client.post(
        "/api/v1/files/",
        data={"biz_type": "resource"},
        files={"file": (filename, payload, "text/plain")},
        headers=headers,
    )
    assert resp.status_code == 200
    return resp.json()["data"]["id"]


def _create_resource(
    client: TestClient,
    headers: dict[str, str],
    *,
    title: str,
    space_id: int,
    file_id: int,
    resource_type: str,
    school_space_id: int | None = None,
) -> int:
    payload = {
        "title": f"{title}_{UNIQUE}",
        "description": "resource for search tests",
        "space_id": space_id,
        "resource_type": resource_type,
        "file_id": file_id,
        "version_note": "v1",
    }
    if school_space_id is not None:
        payload["school_space_id"] = school_space_id

    resp = client.post("/api/v1/resources/", json=payload, headers=headers)
    assert resp.status_code == 200
    return resp.json()["data"]["id"]


def test_search_full_flow_and_scope_filters():
    with TestClient(app) as client:
        headers = _register_and_login(client)

        school_category_id = _create_category(client, headers, "School")
        course_category_id = _create_category(client, headers, "Course")

        school_space_id = _create_space(client, headers, "AlphaSchool", school_category_id)
        course_space_a_id = _create_space(client, headers, "MacroEconomics", course_category_id)
        course_space_b_id = _create_space(client, headers, "MicroEconomics", course_category_id)

        _subscribe_space(client, headers, school_space_id)
        _subscribe_space(client, headers, course_space_a_id)
        _subscribe_space(client, headers, course_space_b_id)

        _create_post(
            client,
            headers,
            title="Economics final review",
            content="macro and micro key points",
            space_id=course_space_a_id,
        )
        _create_post(
            client,
            headers,
            title="Micro economics memory tips",
            content="tips and tricks",
            space_id=course_space_b_id,
        )

        file_a = _upload_file(client, headers, "macro-notes.txt")
        file_b = _upload_file(client, headers, "micro-exam.txt")
        file_c = _upload_file(client, headers, "policy.txt")

        _create_resource(
            client,
            headers,
            title="Economics notes",
            space_id=course_space_a_id,
            school_space_id=school_space_id,
            resource_type="notes",
            file_id=file_a,
        )
        _create_resource(
            client,
            headers,
            title="Economics past exam",
            space_id=course_space_b_id,
            school_space_id=school_space_id,
            resource_type="past_exam",
            file_id=file_b,
        )
        policy_resource_id = _create_resource(
            client,
            headers,
            title="Economics school policy",
            space_id=course_space_a_id,
            school_space_id=school_space_id,
            resource_type="policy",
            file_id=file_c,
        )

        post_search = client.get("/api/v1/search/posts", params={"keyword": "economics review"})
        assert post_search.status_code == 200
        post_data = post_search.json()["data"]
        assert post_data["pagination"]["total"] >= 1
        assert any("Economics final review" in item["title"] for item in post_data["items"])

        loose_search = client.get("/api/v1/search/posts", params={"keyword": "economics randomword"})
        assert loose_search.status_code == 200
        assert loose_search.json()["data"]["pagination"]["total"] >= 1

        space_search = client.get("/api/v1/search/spaces", params={"query": "economics"})
        assert space_search.status_code == 200
        assert space_search.json()["data"]["pagination"]["total"] >= 2

        materials_search = client.get(
            "/api/v1/search/resources",
            params={"keyword": "economics", "scope": "materials"},
        )
        assert materials_search.status_code == 200
        material_items = materials_search.json()["data"]["items"]
        assert len(material_items) >= 2
        assert all(item["resource_type"] != "policy" for item in material_items)

        explore_search = client.get(
            "/api/v1/search/resources",
            params={"keyword": "economics", "scope": "explore"},
        )
        assert explore_search.status_code == 200
        explore_items = explore_search.json()["data"]["items"]
        assert len(explore_items) >= 1
        assert all(item["resource_type"] == "policy" for item in explore_items)
        assert any(item["id"] == policy_resource_id for item in explore_items)

        by_course = client.get(
            "/api/v1/search/resources",
            params={"scope": "materials", "course_space_id": course_space_a_id},
        )
        assert by_course.status_code == 200
        by_course_items = by_course.json()["data"]["items"]
        assert len(by_course_items) >= 1
        assert all(item["course_space_id"] == course_space_a_id for item in by_course_items)

        by_school = client.get(
            "/api/v1/search/resources",
            params={"scope": "materials", "school_space_id": school_space_id},
        )
        assert by_school.status_code == 200
        by_school_items = by_school.json()["data"]["items"]
        assert len(by_school_items) >= 1
        assert all(item["school_space_id"] == school_space_id for item in by_school_items)

        by_space_union = client.get(
            "/api/v1/search/resources",
            params={"scope": "materials", "space_id": school_space_id},
        )
        assert by_space_union.status_code == 200
        assert by_space_union.json()["data"]["pagination"]["total"] >= 1

        no_match = client.get("/api/v1/search/resources", params={"keyword": "zzzz-no-hit"})
        assert no_match.status_code == 200
        assert no_match.json()["data"]["pagination"]["total"] == 0

        suggestions = client.get("/api/v1/search/suggestions", params={"query": "econ"})
        assert suggestions.status_code == 200
        sugg_data = suggestions.json()["data"]
        assert "spaces" in sugg_data
        assert "posts" in sugg_data
        assert "resources" in sugg_data

        page_check = client.get(
            "/api/v1/search/posts",
            params={"keyword": "economics", "page": 1, "page_size": 1},
        )
        assert page_check.status_code == 200
        pagination = page_check.json()["data"]["pagination"]
        assert pagination["page"] == 1
        assert pagination["page_size"] == 1
