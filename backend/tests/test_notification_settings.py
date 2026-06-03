from fastapi.testclient import TestClient

from app.database import SessionLocal
from app.main import app
from app.models import NotificationSetting


client = TestClient(app)


def test_save_notification_setting_with_masked_webhook():
    response = client.patch(
        "/api/notification-settings?user_id=1",
        json={
            "discord_webhook_url": "https://discord.com/api/webhooks/123456/token",
            "discord_enabled": True,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["discord_configured"] is True
    assert data["discord_enabled"] is True
    assert data["masked_webhook_url"].startswith("https://discord.com/")
    assert data["masked_webhook_url"].endswith("token")


def test_webhook_url_is_encrypted_at_rest():
    user_id = 90909091
    webhook_url = "https://discord.com/api/webhooks/secure/token"

    response = client.patch(
        f"/api/notification-settings?user_id={user_id}",
        json={
            "discord_webhook_url": webhook_url,
            "discord_enabled": True,
        },
    )

    assert response.status_code == 200
    with SessionLocal() as db:
        row = db.query(NotificationSetting).filter(NotificationSetting.user_id == user_id).first()
        assert row is not None
        assert row.discord_webhook_url != webhook_url
        assert not row.discord_webhook_url.startswith("https://discord.com")


def test_discord_test_notification_uses_decrypted_webhook(monkeypatch):
    user_id = 90909092
    webhook_url = "https://discord.com/api/webhooks/decrypted/token"
    sent_urls: list[str] = []

    async def fake_send_discord_webhook(url: str, content: str | None = None, payload: dict | None = None):
        sent_urls.append(url)
        return True, None

    monkeypatch.setattr("app.routers.notifications.send_discord_webhook", fake_send_discord_webhook)
    client.patch(
        f"/api/notification-settings?user_id={user_id}",
        json={
            "discord_webhook_url": webhook_url,
            "discord_enabled": True,
        },
    )

    response = client.post(f"/api/notifications/test-discord?user_id={user_id}")

    assert response.status_code == 200
    assert sent_urls == [webhook_url]
