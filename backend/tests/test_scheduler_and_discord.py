from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app
from app.services.adapters.base import ScrapedProduct


client = TestClient(app)


def unique_user_id() -> int:
    return int(str(uuid4().int)[:8])


def test_shop_crawler_sends_discord_when_webhook_is_enabled(monkeypatch):
    user_id = unique_user_id()
    sent_messages: list[tuple[str, str, str]] = []

    async def fake_send(webhook_url: str, product, keyword_text: str):
        sent_messages.append((webhook_url, product.title, keyword_text))
        return True, None

    monkeypatch.setattr("app.services.shop_crawler.send_discord_product_notification", fake_send)
    monkeypatch.setitem(
        __import__("app.services.shop_crawler", fromlist=["SHOP_FETCHERS"]).SHOP_FETCHERS,
        "offmall",
        lambda keyword, limit: [
            ScrapedProduct(
                shop_code="offmall",
                external_product_id=f"test-recolte-{user_id}",
                title="レコルト ホットプレート",
                price=4290,
                product_url=f"https://example.com/recolte/{user_id}",
                image_url=None,
                category="生活家電",
            )
        ],
    )
    client.patch(
        f"/api/notification-settings?user_id={user_id}",
        json={
            "discord_webhook_url": "https://discord.com/api/webhooks/123456/token",
            "discord_enabled": True,
        },
    )
    client.post("/api/keywords", json={"user_id": user_id, "keyword": "レコルト", "shop_code": "all"})

    response = client.post(f"/api/crawler/run-shop?user_id={user_id}&shop_code=offmall&keyword=レコルト&limit=2")

    assert response.status_code == 200
    assert sent_messages == [
        ("https://discord.com/api/webhooks/123456/token", "レコルト ホットプレート", "レコルト")
    ]
    notifications = client.get(f"/api/notifications?user_id={user_id}").json()
    assert any(item["discord_status"] == "success" for item in notifications)


def test_shop_crawler_records_skip_reason_for_price_filter(monkeypatch):
    user_id = unique_user_id()
    sent_messages: list[str] = []

    async def fake_send(webhook_url: str, product, keyword_text: str):
        sent_messages.append(product.title)
        return True, None

    monkeypatch.setattr("app.services.shop_crawler.send_discord_product_notification", fake_send)
    monkeypatch.setitem(
        __import__("app.services.shop_crawler", fromlist=["SHOP_FETCHERS"]).SHOP_FETCHERS,
        "offmall",
        lambda keyword, limit: [
            ScrapedProduct(
                shop_code="offmall",
                external_product_id=f"test-price-{user_id}",
                title="recolte Hot Plate",
                price=9000,
                product_url=f"https://example.com/price/{user_id}",
                image_url=None,
                category="kitchen",
            )
        ],
    )
    client.patch(
        f"/api/notification-settings?user_id={user_id}",
        json={
            "discord_webhook_url": "https://discord.com/api/webhooks/123456/token",
            "discord_enabled": True,
        },
    )
    client.post(
        "/api/keywords",
        json={
            "user_id": user_id,
            "keyword": "レコルト",
            "shop_code": "all",
            "include_terms": "recolte",
            "max_price": 8000,
        },
    )

    response = client.post(f"/api/crawler/run-shop?user_id={user_id}&shop_code=offmall&keyword=recolte&limit=2")

    assert response.status_code == 200
    assert response.json()["matched_count"] == 1
    assert response.json()["notifications_created"] == 0
    assert sent_messages == []
    notifications = client.get(f"/api/notifications?user_id={user_id}").json()
    assert notifications[0]["discord_status"] == "skipped"
    assert notifications[0]["skip_reason"] == "価格が上限超過: 9,000円 > 8,000円"


def test_scheduler_settings_and_run_due(monkeypatch):
    user_id = unique_user_id()
    calls: list[tuple[int, str, str, int]] = []

    def fake_run_shop_crawler(db, user_id: int, shop_code: str, keyword: str, limit: int):
        calls.append((user_id, shop_code, keyword, limit))
        return {
            "fetched_count": 1,
            "matched_count": 1,
            "notifications_created": 1,
            "duplicates_skipped": 0,
            "status": "success",
            "error_message": None,
        }

    monkeypatch.setattr("app.services.scheduler.run_shop_crawler", fake_run_shop_crawler)

    save_response = client.put(
        f"/api/scheduler/settings?user_id={user_id}",
        json={
            "enabled": True,
            "shop_code": "offmall",
            "keyword": "レコルト",
            "interval_minutes": 5,
            "limit": 3,
        },
    )
    assert save_response.status_code == 200
    assert save_response.json()["enabled"] is True

    run_response = client.post(f"/api/scheduler/run-due?user_id={user_id}")

    assert run_response.status_code == 200
    assert run_response.json()["ran"] is True
    assert calls == [(user_id, "offmall", "レコルト", 3)]
