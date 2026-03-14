import asyncio
import time
import uuid

import pytest
from fastapi.testclient import TestClient

from app.ai_mention.notification_socket import notification_socket_manager
from app.ai_mention.service import ai_mention_service
from app.models.enums import TrustLevel, UserRole
from main import app
from tests.authz_test_utils import register_and_login


@pytest.fixture(autouse=True)
def reset_ai_services():
    asyncio.run(ai_mention_service.reset_for_tests())
    notification_socket_manager.clear()
    yield
    asyncio.run(ai_mention_service.reset_for_tests())
    notification_socket_manager.clear()


def _create_post_with_comment(
    client: TestClient,
    headers: dict[str, str],
    *,
    suffix: str,
    comment_content: str,
) -> tuple[int, int, int]:
    category = client.post(
        "/api/v1/categories/",
        json={"name": f"AI Cat {suffix}"},
        headers=headers,
    )
    assert category.status_code == 200
    category_id = category.json()["data"]["id"]

    space = client.post(
        "/api/v1/spaces/",
        json={"name": f"AI Space {suffix}", "category_id": category_id},
        headers=headers,
    )
    assert space.status_code == 200
    space_id = space.json()["data"]["id"]

    post = client.post(
        "/api/v1/posts/",
        json={
            "title": f"AI Post {suffix}",
            "content": "Post body for AI mention tests.",
            "space_id": space_id,
        },
        headers=headers,
    )
    assert post.status_code == 200
    post_id = post.json()["data"]["id"]

    comment = client.post(
        "/api/v1/comments/",
        json={
            "content": comment_content,
            "post_id": post_id,
        },
        headers=headers,
    )
    assert comment.status_code == 200
    comment_id = comment.json()["data"]["id"]

    return space_id, post_id, comment_id


def _create_comment(client: TestClient, headers: dict[str, str], post_id: int, content: str) -> int:
    comment = client.post(
        "/api/v1/comments/",
        json={
            "content": content,
            "post_id": post_id,
        },
        headers=headers,
    )
    assert comment.status_code == 200
    return comment.json()["data"]["id"]


def _poll_task_status(client: TestClient, headers: dict[str, str], task_id: str, timeout_seconds: float = 8.0) -> str:
    started = time.monotonic()
    latest_status = "queued"

    while time.monotonic() - started < timeout_seconds:
        response = client.get(f"/api/v1/ai-mention/tasks/{task_id}", headers=headers)
        assert response.status_code == 200
        latest_status = response.json()["data"]["status"]
        if latest_status in {"succeeded", "failed", "timeout"}:
            return latest_status
        time.sleep(0.05)

    return latest_status


def test_ai_mention_task_create_idempotent_and_success_notification():
    with TestClient(app) as client:
        headers, _, _ = register_and_login(
            client,
            prefix="ai_user",
            role=UserRole.ADMIN,
            trust_level=TrustLevel.CONTRIBUTOR,
        )
        suffix = uuid.uuid4().hex[:8]
        space_id, post_id, comment_id = _create_post_with_comment(
            client,
            headers,
            suffix=suffix,
            comment_content="plain top-level comment",
        )

        create_response = client.post(
            "/api/v1/ai-mention/tasks",
            json={
                "comment_id": comment_id,
                "post_id": post_id,
                "space_id": space_id,
                "comment_content": "@ai summarize the post in 3 bullets",
            },
            headers=headers,
        )
        assert create_response.status_code == 200
        payload = create_response.json()
        assert payload["message"] == "task queued"
        task_id = payload["data"]["id"]

        duplicate = client.post(
            "/api/v1/ai-mention/tasks",
            json={
                "comment_id": comment_id,
                "post_id": post_id,
                "space_id": space_id,
                "comment_content": "@ai rerun",
            },
            headers=headers,
        )
        assert duplicate.status_code == 200
        assert duplicate.json()["message"] == "task already exists"
        assert duplicate.json()["data"]["id"] == task_id

        final_status = _poll_task_status(client, headers, task_id)
        assert final_status == "succeeded"

        notifications = client.get("/api/v1/me/notifications", headers=headers)
        assert notifications.status_code == 200
        items = notifications.json()["data"]["items"]
        assert any(item["type"] == "ai_reply" for item in items)


def test_ai_mention_task_failed_and_timeout_paths():
    original_timeout = ai_mention_service._timeout_seconds
    original_retries = ai_mention_service._max_retries
    ai_mention_service._timeout_seconds = 0.05
    ai_mention_service._max_retries = 0

    try:
        with TestClient(app) as client:
            headers, _, _ = register_and_login(
                client,
                prefix="ai_user",
                role=UserRole.ADMIN,
                trust_level=TrustLevel.CONTRIBUTOR,
            )
            suffix = uuid.uuid4().hex[:8]
            space_id, post_id, failed_comment_id = _create_post_with_comment(
                client,
                headers,
                suffix=suffix,
                comment_content="plain baseline comment",
            )
            timeout_comment_id = _create_comment(client, headers, post_id, "plain timeout comment")

            failed_response = client.post(
                "/api/v1/ai-mention/tasks",
                json={
                    "comment_id": failed_comment_id,
                    "post_id": post_id,
                    "space_id": space_id,
                    "prompt": "[fail] break this task",
                },
                headers=headers,
            )
            assert failed_response.status_code == 200
            failed_id = failed_response.json()["data"]["id"]
            failed_status = _poll_task_status(client, headers, failed_id)
            assert failed_status == "failed"

            timeout_response = client.post(
                "/api/v1/ai-mention/tasks",
                json={
                    "comment_id": timeout_comment_id,
                    "post_id": post_id,
                    "space_id": space_id,
                    "prompt": "[timeout] let this timeout",
                },
                headers=headers,
            )
            assert timeout_response.status_code == 200
            timeout_id = timeout_response.json()["data"]["id"]
            timeout_status = _poll_task_status(client, headers, timeout_id, timeout_seconds=3)
            assert timeout_status == "timeout"

    finally:
        ai_mention_service._timeout_seconds = original_timeout
        ai_mention_service._max_retries = original_retries


def test_top_level_comment_with_ai_mention_auto_creates_reply_and_notification():
    with TestClient(app) as client:
        headers, _, _ = register_and_login(
            client,
            prefix="ai_user",
            role=UserRole.ADMIN,
            trust_level=TrustLevel.CONTRIBUTOR,
        )
        suffix = uuid.uuid4().hex[:8]
        _, post_id, comment_id = _create_post_with_comment(
            client,
            headers,
            suffix=suffix,
            comment_content="@ai summarize the post and list next steps",
        )

        started = time.monotonic()
        ai_reply_comment_id = None
        found_ai_notification = False

        while time.monotonic() - started < 5:
            comments_resp = client.get(f"/api/v1/comments/post/{post_id}")
            assert comments_resp.status_code == 200
            items = comments_resp.json()["data"]["items"]
            for item in items:
                if item.get("parent_id") == comment_id:
                    ai_reply_comment_id = item["id"]
                    break

            notifications = client.get("/api/v1/me/notifications", headers=headers)
            assert notifications.status_code == 200
            notification_items = notifications.json()["data"]["items"]
            if any(
                item.get("type") == "ai_reply"
                and ai_reply_comment_id is not None
                and item.get("target_id") == ai_reply_comment_id
                for item in notification_items
            ):
                found_ai_notification = True

            if ai_reply_comment_id is not None and found_ai_notification:
                break
            time.sleep(0.1)

        assert ai_reply_comment_id is not None
        assert found_ai_notification


def test_nested_comment_cannot_trigger_ai():
    with TestClient(app) as client:
        headers, _, _ = register_and_login(
            client,
            prefix="ai_user",
            role=UserRole.ADMIN,
            trust_level=TrustLevel.CONTRIBUTOR,
        )
        suffix = uuid.uuid4().hex[:8]
        _, post_id, comment_id = _create_post_with_comment(
            client,
            headers,
            suffix=suffix,
            comment_content="plain top-level comment",
        )

        reply = client.post(
            "/api/v1/comments/",
            json={
                "content": "@ai answer this nested question",
                "post_id": post_id,
                "parent_id": comment_id,
            },
            headers=headers,
        )
        assert reply.status_code == 400
        assert "@ai" in reply.json()["message"]

        comments_resp = client.get(f"/api/v1/comments/post/{post_id}")
        assert comments_resp.status_code == 200
        items = comments_resp.json()["data"]["items"]
        assert len(items) == 1
        assert items[0]["id"] == comment_id
