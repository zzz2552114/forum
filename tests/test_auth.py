import uuid

from fastapi.testclient import TestClient

from main import app


def test_register_login_and_authorization_snapshot():
    with TestClient(app) as client:
        username = f"testuser_authz_{uuid.uuid4().hex[:8]}"

        # Register user
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": username,
                "email": f"{username}@example.com",
                "password": "testpassword123",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == username
        assert data["email"] == f"{username}@example.com"
        assert data["role"] == "user"

        # Login
        login_response = client.post(
            "/api/v1/auth/login",
            data={"username": username, "password": "testpassword123"},
        )
        assert login_response.status_code == 200
        token_data = login_response.json()
        assert "access_token" in token_data
        assert token_data["token_type"] == "bearer"

        headers = {"Authorization": f"Bearer {token_data['access_token']}"}

        # Authorization snapshot defaults to BASIC user
        authz = client.get("/api/v1/me/authorization", headers=headers)
        assert authz.status_code == 200
        snapshot = authz.json()["data"]
        assert snapshot["auth_state"] == "auth"
        assert snapshot["role"] == "user"
        assert snapshot["trust_level"] == 1
        assert "post.create" in snapshot["permissions"]

        # Wrong password should fail
        wrong_login_response = client.post(
            "/api/v1/auth/login",
            data={"username": username, "password": "wrongpassword"},
        )
        assert wrong_login_response.status_code == 401
        assert wrong_login_response.json()["message"] == "Incorrect username or password"


def test_guest_authorization_and_write_forbidden():
    with TestClient(app) as client:
        guest_authz = client.get("/api/v1/me/authorization")
        assert guest_authz.status_code == 200
        snapshot = guest_authz.json()["data"]
        assert snapshot["auth_state"] == "guest"
        assert snapshot["role"] == "guest"
        assert snapshot["trust_level"] == 0

        # Guest cannot write
        denied = client.post(
            "/api/v1/posts/",
            json={"title": "x", "content": "x", "space_id": 1},
        )
        assert denied.status_code == 403
        payload = denied.json()
        assert payload["data"]["required_permission"] == "auth.login"
        assert payload["data"]["required_trust_level"] == 1


def test_invalid_token_handling():
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/spaces/",
            json={"name": "test", "category_id": 1},
            headers={"Authorization": "Bearer not_a_real_token_123"},
        )
        assert response.status_code == 401
