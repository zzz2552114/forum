import asyncio
import time
import uuid

from fastapi.testclient import TestClient

from app.ai_mention.notification_socket import notification_socket_manager
from app.ai_mention.service import ai_mention_service
from app.models.enums import TrustLevel, UserRole
from main import app
from tests.authz_test_utils import register_and_login


def _create_space_and_post(client: TestClient, headers: dict[str, str], suffix: str) -> tuple[int, int]:
    category = client.post(
        "/api/v1/categories/",
        json={"name": f"Notify Cat {suffix}"},
        headers=headers,
    )
    assert category.status_code == 200
    category_id = category.json()["data"]["id"]

    space = client.post(
        "/api/v1/spaces/",
        json={"name": f"Notify Space {suffix}", "category_id": category_id},
        headers=headers,
    )
    assert space.status_code == 200
    space_id = space.json()["data"]["id"]

    post = client.post(
        "/api/v1/posts/",
        json={
            "title": f"Notify Post {suffix}",
            "content": "Notification flow test post",
            "space_id": space_id,
        },
        headers=headers,
    )
    assert post.status_code == 200
    post_id = post.json()["data"]["id"]

    return space_id, post_id


def test_notification_events_like_bookmark_reply_and_chat_mention():
    asyncio.run(ai_mention_service.reset_for_tests())
    notification_socket_manager.clear()

    with TestClient(app) as client:
        alice_headers, alice_token, alice_username = register_and_login(
            client,
            prefix="alice",
            role=UserRole.ADMIN,
            trust_level=TrustLevel.CONTRIBUTOR,
        )
        bob_headers, bob_token, bob_username = register_and_login(
            client,
            prefix="bob",
            role=UserRole.USER,
            trust_level=TrustLevel.BASIC,
        )

        suffix = uuid.uuid4().hex[:6]
        space_id, post_id = _create_space_and_post(client, alice_headers, suffix)

        sub_resp = client.put(f"/api/v1/spaces/{space_id}/subscriptions/me", headers=bob_headers)
        assert sub_resp.status_code == 200

        like_resp = client.put(f"/api/v1/posts/{post_id}/likes/me", headers=bob_headers)
        assert like_resp.status_code == 200

        bookmark_resp = client.put(f"/api/v1/posts/{post_id}/bookmarks/me", headers=bob_headers)
        assert bookmark_resp.status_code == 200

        comment_resp = client.post(
            "/api/v1/comments/",
            json={"content": "nice post", "post_id": post_id},
            headers=bob_headers,
        )
        assert comment_resp.status_code == 200

        notifications = client.get("/api/v1/me/notifications", headers=alice_headers)
        assert notifications.status_code == 200
        types = {item["type"] for item in notifications.json()["data"]["items"]}
        assert "post_like" in types
        assert "post_bookmark" in types
        assert "comment_reply" in types

        with client.websocket_connect(f"/ws/notifications?token={alice_token}") as alice_ws:
            alice_ws.send_text("ping")
            pong = alice_ws.receive_json()
            assert pong["type"] == "pong"

            with client.websocket_connect(
                f"/ws/chat/{space_id}/2?username={bob_username}&token={bob_token}"
            ) as bob_chat:
                bob_chat.receive_json()  # join presence
                bob_chat.send_json({"content": f"@{alice_username} check this room"})
                bob_chat.receive_json()  # chat echo

                event = alice_ws.receive_json()
                assert event["type"] == "notification"
                assert event["notification_type"] == "chat_mention"
                assert event["target_type"] == "space"
                assert event["target_id"] == space_id


def test_comment_ai_mention_creates_reply_comment_and_notification():
    asyncio.run(ai_mention_service.reset_for_tests())
    notification_socket_manager.clear()

    with TestClient(app) as client:
        headers, _, _ = register_and_login(
            client,
            prefix="aiowner",
            role=UserRole.ADMIN,
            trust_level=TrustLevel.CONTRIBUTOR,
        )
        suffix = uuid.uuid4().hex[:6]
        space_id, post_id = _create_space_and_post(client, headers, suffix)

        comment_resp = client.post(
            "/api/v1/comments/",
            json={
                "content": "@ai provide a short action list",
                "post_id": post_id,
            },
            headers=headers,
        )
        assert comment_resp.status_code == 200
        comment_id = comment_resp.json()["data"]["id"]

        started = time.monotonic()
        found_ai_reply = False
        found_ai_notification = False
        ai_reply_comment_id = None

        while time.monotonic() - started < 5:
            comments_resp = client.get(f"/api/v1/comments/post/{post_id}")
            assert comments_resp.status_code == 200
            items = comments_resp.json()["data"]["items"]
            for item in items:
                if item.get("parent_id") == comment_id:
                    found_ai_reply = True
                    ai_reply_comment_id = item["id"]

            notifications_resp = client.get("/api/v1/me/notifications", headers=headers)
            assert notifications_resp.status_code == 200
            notification_items = notifications_resp.json()["data"]["items"]
            if any(
                item.get("type") == "ai_reply" and ai_reply_comment_id is not None and item.get("target_id") == ai_reply_comment_id
                for item in notification_items
            ):
                found_ai_notification = True

            if found_ai_reply and found_ai_notification:
                break
            time.sleep(0.1)

        assert found_ai_reply
        assert ai_reply_comment_id is not None
        assert found_ai_notification
