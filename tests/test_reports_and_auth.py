import uuid
from fastapi.testclient import TestClient

from main import app
from tests.authz_test_utils import register_and_login, create_category_and_space
from app.models.enums import UserRole, TrustLevel

def test_student_authentication_flow():
    with TestClient(app) as client:
        # Register a normal user
        headers, token, username = register_and_login(client, prefix="stu_auth")
        
        # 1. Test invalid email
        resp = client.post(
            "/api/v1/auth/stu-auth/send", 
            json={"school_name": "Test University", "email": "invalid@gmail.com"}, 
            headers=headers
        )
        assert resp.status_code == 200
        assert resp.json()["data"]["success"] is False
        
        # 2. Test valid email
        resp = client.post(
            "/api/v1/auth/stu-auth/send", 
            json={"school_name": "Test University", "email": "valid@test.edu.cn"}, 
            headers=headers
        )
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["success"] is True
        code = data["code"]
        
        # 3. Test wrong code
        resp = client.post(
            "/api/v1/auth/stu-auth/verify", 
            json={"code": "000000"}, 
            headers=headers
        )
        assert resp.status_code == 200
        assert resp.json()["data"]["success"] is False
        
        # 4. Test right code
        resp = client.post(
            "/api/v1/auth/stu-auth/verify", 
            json={"code": code}, 
            headers=headers
        )
        assert resp.status_code == 200
        assert resp.json()["data"]["success"] is True
        
        # 5. Verify user trust level upgraded
        authz = client.get("/api/v1/me/authorization", headers=headers)
        assert authz.json()["data"]["trust_level"] >= 2 # VERIFIED

def test_reports_flow():
    with TestClient(app) as client:
        # Create reporter (user)
        reporter_headers, _, reporter_name = register_and_login(client, prefix="reporter")
        
        # Create admin
        admin_headers, _, admin_name = register_and_login(
            client, prefix="admin_rep", role=UserRole.ADMIN, trust_level=TrustLevel.CONTRIBUTOR
        )
        
        # Create a post to report
        cat_id, space_id = create_category_and_space(
            client, admin_headers, suffix="rep", category_name="Cat", space_name="Space"
        )
        
        # Reporter needs to subscribe space to post
        client.put(f"/api/v1/spaces/{space_id}/subscriptions/me", headers=reporter_headers)
        
        post_resp = client.post(
            "/api/v1/posts/", 
            json={"title": "Bad Post", "content": "Spam", "space_id": space_id}, 
            headers=reporter_headers
        )
        assert post_resp.status_code == 200, post_resp.json()
        post_id = post_resp.json()["data"]["id"]
        
        # 1. Reporter reports the post
        rep_resp = client.post(
            "/api/v1/reports/", 
            json={"reason": "spam", "post_id": post_id}, 
            headers=reporter_headers
        )
        assert rep_resp.status_code == 200, rep_resp.json()
        report_id = rep_resp.json()["data"]["id"]
        assert rep_resp.json()["data"]["status"] == "pending"
        
        # 2. Reporter gets their own report
        my_rep = client.get(f"/api/v1/reports/{report_id}", headers=reporter_headers)
        assert my_rep.status_code == 200
        assert my_rep.json()["data"]["reason"] == "spam"
        
        # 3. Another user cannot get reporter's report
        other_headers, _, _ = register_and_login(client, prefix="other")
        other_rep = client.get(f"/api/v1/reports/{report_id}", headers=other_headers)
        assert other_rep.status_code == 403
        
        # 4. Admin updates the report
        update_resp = client.put(
            f"/api/v1/reports/{report_id}", 
            json={"status": "approved"}, 
            headers=admin_headers
        )
        assert update_resp.status_code == 200, update_resp.json()
        assert update_resp.json()["data"]["status"] == "approved"
        
        # 5. Verify reporter sees the updated status
        my_rep_after = client.get(f"/api/v1/reports/{report_id}", headers=reporter_headers)
        assert my_rep_after.json()["data"]["status"] == "approved"
