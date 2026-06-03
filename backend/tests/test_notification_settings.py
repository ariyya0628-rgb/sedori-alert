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
