import io
import os
import uuid
import pytest
from fastapi.testclient import TestClient
from PIL import Image
from main import app
from tests.authz_test_utils import register_and_login

def create_test_image():
    file = io.BytesIO()
    image = Image.new('RGB', (100, 100), color=(73, 109, 137))
    image.save(file, 'png')
    file.name = 'test.png'
    file.seek(0)
    return file

def test_files_upload_and_validation():
    with TestClient(app) as client:
        # 1. Setup User (Trust level 1 by default via register_and_login)
        headers, _, _ = register_and_login(
            client,
            prefix="files_test",
        )

        # 2. Test /files/avatar Success
        img_file = create_test_image()
        response = client.post(
            "/api/v1/files/avatar",
            headers=headers,
            files={"file": ("avatar.png", img_file, "image/png")}
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert "avatars" in data["url"]
        
        # Verify physical file existence
        local_path = data["url"].replace("/static/", "")
        assert os.path.exists(local_path)
        
        # 3. Test /files/avatar Failure (Invalid Image)
        bad_file = io.BytesIO(b"this is not an image content")
        response = client.post(
            "/api/v1/files/avatar",
            headers=headers,
            files={"file": ("fake.png", bad_file, "image/png")}
        )
        assert response.status_code == 400
        assert "Invalid image file format" in response.json()["detail"]
        
        # 4. Test /files/ (General Upload - Success due to ENABLE_LOCAL_TESTING=true)
        img_file_2 = create_test_image()
        response = client.post(
            "/api/v1/files/",
            headers=headers,
            files={"file": ("general.png", img_file_2, "image/png")}
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert "general" in data["url"]
        
        # 5. Test Delete
        file_id = data["id"]
        local_file_path = data["url"].replace("/static/", "")
        assert os.path.exists(local_file_path)
        
        del_resp = client.delete(f"/api/v1/files/{file_id}", headers=headers)
        assert del_resp.status_code == 200
        
        # Verify file is gone from disk
        assert not os.path.exists(local_file_path)

def test_upload_file_unauthorized():
    with TestClient(app) as client:
        img_file = create_test_image()
        response = client.post(
            "/api/v1/files/avatar",
            files={"file": ("unauth.png", img_file, "image/png")}
        )
        assert response.status_code == 401
