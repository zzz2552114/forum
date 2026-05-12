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


def _create_post_and_comment(
    client: TestClient,
    headers: dict[str, str],
    suffix: str,
    *,
    comment_content: str = "plain top-level comment",
) -> tuple[int, int, int]:
    category = client.post(
        "/api/v1/categories/",
        json={"name": f"WS Cat {suffix}"},
        headers=headers,
    )
    assert category.status_code == 200
    category_id = category.json()["data"]["id"]

    space = client.post(
        "/api/v1/spaces/",
        json={"name": f"WS Space {suffix}", "category_id": category_id},
        headers=headers,
    )
    assert space.status_code == 200
    space_id = space.json()["data"]["id"]

    post = client.post(
        "/api/v1/posts/",
        json={
            "title": f"WS Post {suffix}",
            "content": "post content",
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


def test_notification_websocket_pushes_ai_task_event():
    with TestClient(app) as client:
        headers, token, _ = register_and_login(
            client,
            prefix="ws_user",
            role=UserRole.ADMIN,
            trust_level=TrustLevel.CONTRIBUTOR,
        )
        suffix = uuid.uuid4().hex[:8]
        space_id, post_id, comment_id = _create_post_and_comment(client, headers, suffix)

        with client.websocket_connect(f"/ws/notifications?token={token}") as ws:
            ws.send_text("ping")
            pong = ws.receive_json()
            assert pong["type"] == "pong"

            create_response = client.post(
                "/api/v1/ai-mention/tasks",
                json={
                    "comment_id": comment_id,
                    "post_id": post_id,
                    "space_id": space_id,
                    "prompt": "please generate action summary",
                },
                headers=headers,
            )
            assert create_response.status_code == 200
            task_id = create_response.json()["data"]["id"]

            started = time.monotonic()
            event = None
            while time.monotonic() - started < 3:
                next_payload = ws.receive_json()
                if next_payload.get("type") == "notification":
                    event = next_payload
                    break

            assert event is not None
            assert event["task_id"] == task_id
            assert event["task_status"] in {"succeeded", "failed", "timeout"}
            assert event["notification_type"] == "ai_reply"
            assert event["target_type"] == "comment"
            assert event["reply_comment_id"] is not None
            assert event["target_id"] != comment_id
            assert event["target_id"] == event["reply_comment_id"]
            assert event["extra_payload"]["comment_id"] == comment_id
