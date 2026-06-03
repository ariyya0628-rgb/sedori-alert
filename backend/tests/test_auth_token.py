from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_auth_me_requires_valid_bearer_token():
    missing_response = client.get("/api/auth/me")
    assert missing_response.status_code == 401

    invalid_response = client.get("/api/auth/me", headers={"Authorization": "Bearer invalid-token"})
    assert invalid_response.status_code == 401


def test_auth_me_returns_logged_in_user():
    login_response = client.post(
        "/api/auth/login",
        json={"email": "admin@example.com", "password": "password123"},
    )
    token = login_response.json()["access_token"]

    response = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    assert response.json()["email"] == "admin@example.com"
    assert response.json()["user_id"] == login_response.json()["user_id"]
