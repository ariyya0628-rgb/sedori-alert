from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_create_and_list_keyword():
    response = client.post("/api/keywords", json={"user_id": 1, "keyword": "レコルト", "shop_code": "all"})
    assert response.status_code == 200
    created = response.json()
    assert created["keyword"] == "レコルト"
    assert created["shop_code"] == "all"
    assert created["enabled"] is True

    list_response = client.get("/api/keywords?user_id=1")
    assert list_response.status_code == 200
    keywords = list_response.json()
    assert any(item["keyword"] == "レコルト" for item in keywords)
