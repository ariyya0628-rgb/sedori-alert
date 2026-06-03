from fastapi.testclient import TestClient
from uuid import uuid4

from app.main import app


client = TestClient(app)


def test_mock_crawler_matches_keyword_and_skips_duplicate_notification():
    user_id = int(str(uuid4().int)[:8])
    client.post("/api/keywords", json={"user_id": user_id, "keyword": "レコルト", "shop_code": "all"})

    first_response = client.post(f"/api/crawler/run-mock?user_id={user_id}")
    assert first_response.status_code == 200
    first = first_response.json()
    assert first["fetched_count"] >= 1
    assert first["matched_count"] >= 1
    assert first["notifications_created"] >= 1

    second_response = client.post(f"/api/crawler/run-mock?user_id={user_id}")
    assert second_response.status_code == 200
    second = second_response.json()
    assert second["fetched_count"] == first["fetched_count"]
    assert second["matched_count"] == first["matched_count"]
    assert second["notifications_created"] == 0
    assert second["duplicates_skipped"] >= 1


def test_products_and_crawl_logs_are_listed_after_mock_crawl():
    client.post("/api/crawler/run-mock?user_id=1")

    products_response = client.get("/api/products")
    assert products_response.status_code == 200
    products = products_response.json()
    assert any(product["title"] == "レコルト ホットプレート" for product in products)

    logs_response = client.get("/api/crawl-logs")
    assert logs_response.status_code == 200
    logs = logs_response.json()
    assert len(logs) >= 1
    assert logs[0]["shop_code"] == "mock"
