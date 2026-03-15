import re
import uuid
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from app.models.enums import TrustLevel, UserRole
from main import app as main_app
from tests.authz_test_utils import register_and_login
from app.realtime_chat.endpoint import router as realtime_chat_router
from app.realtime_chat.manager import connection_manager

TIME_PATTERN = re.compile(r"^\d{2}-\d{2} \d{2}:\d{2}$")

def create_test_app() -> FastAPI:
    return main_app

@pytest.fixture(autouse=True)
def clear_connections():
    connection_manager.clear()
    yield
    connection_manager.clear()


def _setup_space_and_user(client: TestClient, suffix: str):
    headers, token, user = register_and_login(
        client,
        prefix=f"chat_{suffix}",
        role=UserRole.ADMIN,
        trust_level=TrustLevel.CONTRIBUTOR,
    )
    
    cat_resp = client.post("/api/v1/categories/", json={"name": f"Chat Cat {suffix}"}, headers=headers)
    cat_id = cat_resp.json()["data"]["id"]
    
    space_resp = client.post("/api/v1/spaces/", json={"name": f"Chat Space {suffix}", "category_id": cat_id}, headers=headers)
    space_id = space_resp.json()["data"]["id"]
    
    client.put(f"/api/v1/spaces/{space_id}/subscriptions/me", headers=headers)
    return headers, token, user, space_id


def assert_time_payload(message: dict) -> None:
    assert "timestamp" in message
    assert isinstance(message["timestamp"], str)
    assert TIME_PATTERN.match(message["display_time"])


def test_websocket_rejects_empty_username():
    app = create_test_app()
    with TestClient(app) as client:
        with client.websocket_connect("/ws/chat?username=   ") as socket:
            with pytest.raises(WebSocketDisconnect) as exc:
                socket.receive_json()

    assert exc.value.code == 1008


def test_websocket_broadcasts_join_chat_leave_events():
    app = create_test_app()
    with TestClient(app) as client:
        with client.websocket_connect("/ws/chat?username=alice") as alice:
            alice_joined = alice.receive_json()
            assert alice_joined["type"] == "system"
            assert "alice joined" in alice_joined["content"]
            assert alice_joined["online_count"] == 1
            assert_time_payload(alice_joined)

            with client.websocket_connect("/ws/chat?username=bob") as bob:
                bob_join_for_alice = alice.receive_json()
                bob_join_for_bob = bob.receive_json()

                assert "bob joined" in bob_join_for_alice["content"]
                assert bob_join_for_alice["online_count"] == 2
                assert "bob joined" in bob_join_for_bob["content"]
                assert bob_join_for_bob["online_count"] == 2

                bob.send_json({"content": "hello everyone"})
                chat_for_alice = alice.receive_json()
                chat_for_bob = bob.receive_json()

                assert chat_for_alice["type"] == "chat"
                assert chat_for_alice["username"] == "bob"
                assert chat_for_alice["content"] == "hello everyone"
                assert chat_for_bob["type"] == "chat"
                assert_time_payload(chat_for_alice)

            bob_left = alice.receive_json()
            assert bob_left["type"] == "system"
            assert "bob left" in bob_left["content"]
            assert bob_left["online_count"] == 1
            assert_time_payload(bob_left)


def test_websocket_validates_message_content():
    app = create_test_app()
    with TestClient(app) as client:
        with client.websocket_connect("/ws/chat?username=alice") as alice:
            alice.receive_json()

            alice.send_json({"content": "   "})
            empty_payload = alice.receive_json()
            assert empty_payload["type"] == "system"
            assert "\u6d88\u606f\u5185\u5bb9\u4e0d\u80fd\u4e3a\u7a7a" in empty_payload["content"]
            assert empty_payload["online_count"] == 1

            alice.send_json({"content": "x" * 501})
            too_long_payload = alice.receive_json()
            assert too_long_payload["type"] == "system"
            assert "\u6700\u591a\u5141\u8bb8 500 \u4e2a\u5b57\u7b26" in too_long_payload["content"]
            assert too_long_payload["online_count"] == 1


def test_room_websocket_rejects_empty_username():
    app = create_test_app()
    with TestClient(app) as client:
        with client.websocket_connect("/ws/chat/1/1?username=   ") as socket:
            with pytest.raises(WebSocketDisconnect) as exc:
                socket.receive_json()

    assert exc.value.code == 1008


def test_room_isolated_by_space_and_section():
    app = create_test_app()
    with TestClient(app) as client:
        suffix = uuid.uuid4().hex[:6]
        _, alice_token, alice_username, space1_id = _setup_space_and_user(client, f"alice_{suffix}")
        _, bob_token, bob_username, space2_id = _setup_space_and_user(client, f"bob_{suffix}")

        with client.websocket_connect(f"/ws/chat/{space1_id}/10?username={alice_username}&token={alice_token}") as alice:
            alice_joined = alice.receive_json()
            assert alice_joined["type"] == "presence"
            assert alice_joined["room"] == f"{space1_id}:10"

            with client.websocket_connect(f"/ws/chat/{space2_id}/10?username={bob_username}&token={bob_token}") as bob:
                bob_joined = bob.receive_json()
                assert bob_joined["type"] == "presence"
                assert bob_joined["room"] == f"{space2_id}:10"

                bob.send_json({"content": "hello from room 2"})
                bob_chat = bob.receive_json()
                assert bob_chat["type"] == "chat"
                assert bob_chat["room"] == f"{space2_id}:10"
                assert bob_chat["content"] == "hello from room 2"

                alice.send_json({"content": "hello from room 1"})
                alice_chat = alice.receive_json()
                assert alice_chat["type"] == "chat"
                assert alice_chat["room"] == f"{space1_id}:10"
                assert alice_chat["username"] == alice_username
                assert alice_chat["content"] == "hello from room 1"


def test_room_history_replay_from_last_event_id():
    app = create_test_app()
    with TestClient(app) as client:
        suffix = uuid.uuid4().hex[:6]
        alice_headers, alice_token, alice_username, space_id = _setup_space_and_user(client, f"alice_{suffix}")
        _, bob_token, bob_username, _ = _setup_space_and_user(client, f"bob_{suffix}")
        
        # Make bob join the SAME space
        client.put(f"/api/v1/spaces/{space_id}/subscriptions/me", headers=alice_headers) # actually bob should subscribe but alice admin is fine. Let's make bob explicitly subscribe
        
        bob_headers, _, _ = register_and_login(client, prefix=f"bobs_sub_{suffix}", role=UserRole.USER, trust_level=TrustLevel.BASIC)
        client.put(f"/api/v1/spaces/{space_id}/subscriptions/me", headers=bob_headers)

        with client.websocket_connect(f"/ws/chat/{space_id}/9?username={alice_username}&token={alice_token}") as alice:
            joined_event = alice.receive_json()
            joined_id = joined_event["event_id"]

            alice.send_json({"content": "m1"})
            alice.receive_json()

            alice.send_json({"content": "m2"})
            alice.receive_json()

        with client.websocket_connect(f"/ws/chat/{space_id}/9?username={bob_username}&token={bob_token}&last_event_id={joined_id}") as bob:
            history_event = bob.receive_json()
            assert history_event["type"] == "history"
            assert history_event["room"] == f"{space_id}:9"

            replayed = history_event["payload"]["events"]
            assert len(replayed) >= 2
            assert all(event["event_id"] > joined_id for event in replayed)
            assert all(event["room"] == f"{space_id}:9" for event in replayed)

            bob_joined = bob.receive_json()
            assert bob_joined["type"] == "presence"
            assert f"{bob_username} joined" in bob_joined["message"]


def test_room_rate_limit_and_ping_pong():
    app = create_test_app()
    with TestClient(app) as client:
        suffix = uuid.uuid4().hex[:6]
        _, alice_token, alice_username, space_id = _setup_space_and_user(client, f"alice_{suffix}")

        with client.websocket_connect(f"/ws/chat/{space_id}/8?username={alice_username}&token={alice_token}") as alice:
            alice.receive_json()

            alice.send_json({"type": "ping"})
            pong = alice.receive_json()
            assert pong["type"] == "presence"
            assert pong["message"] == "pong"

            rate_limited = False
            for idx in range(20):
                alice.send_json({"content": f"msg-{idx}"})
                response = alice.receive_json()
                if response["type"] == "error":
                    assert "\u53d1\u9001\u8fc7\u4e8e\u9891\u7e41" in response["message"]
                    rate_limited = True
                    break

            assert rate_limited
