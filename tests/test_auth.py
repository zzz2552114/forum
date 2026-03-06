import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_register_and_login():
    # TestClient context manager runs startup and shutdown events automatically
    with TestClient(app) as client:
        # Create unique username to avoid DB collisions if tests fail mid-way
        import uuid
        unique_suffix = str(uuid.uuid4())[:8]
        username = f"testuser_{unique_suffix}"
        
        # 1. Register a test user
        response = client.post("/api/v1/auth/register", json={
            "username": username,
            "email": f"{username}@example.com",
            "password": "testpassword123"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == username
        assert data["email"] == f"{username}@example.com"
        assert "id" in data
        
        # 2. Login the test user
        login_response = client.post("/api/v1/auth/login", data={
            "username": username,
            "password": "testpassword123"
        })
        assert login_response.status_code == 200
        token_data = login_response.json()
        assert "access_token" in token_data
        assert token_data["token_type"] == "bearer"
