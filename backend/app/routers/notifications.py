from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Notification, NotificationSetting
from app.schemas import NotificationResponse
from app.services.discord import send_discord_webhook


router = APIRouter(prefix="/api/notifications", tags=["notifications"])


@router.get("", response_model=list[NotificationResponse])
def list_notifications(user_id: int = Query(...), db: Session = Depends(get_db)):
    return (
        db.query(Notification)
        .filter(Notification.user_id == user_id)
        .order_by(Notification.notified_at.desc())
        .all()
    )


@router.post("/test-discord")
async def test_discord(user_id: int = Query(...), db: Session = Depends(get_db)):
    setting = db.query(NotificationSetting).filter(NotificationSetting.user_id == user_id).first()
    if not setting or not setting.discord_webhook_url or not setting.discord_enabled:
        raise HTTPException(status_code=400, detail="Discord notification is not configured")

    ok, error = await send_discord_webhook(
        setting.discord_webhook_url,
        "せどり新着アラートのテスト通知です。",
    )
    row = Notification(
        user_id=user_id,
        shop_code="manual",
        product_title="Discord test notification",
        product_url="https://example.com",
        matched_keyword="test",
        discord_status="success" if ok else "failed",
        discord_error=error,
    )
    db.add(row)
    db.commit()
    if not ok:
        raise HTTPException(status_code=502, detail=error)
    return {"sent": True}
