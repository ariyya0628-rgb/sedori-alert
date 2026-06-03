from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import NotificationSetting
from app.schemas import NotificationSettingRequest, NotificationSettingResponse
from app.services.discord import mask_webhook_url
from app.services.secrets import decrypt_secret, encrypt_secret
from app.time_utils import utc_now


router = APIRouter(prefix="/api/notification-settings", tags=["notification-settings"])


@router.get("", response_model=NotificationSettingResponse)
def get_notification_setting(user_id: int = Query(...), db: Session = Depends(get_db)):
    row = db.query(NotificationSetting).filter(NotificationSetting.user_id == user_id).first()
    if not row:
        return NotificationSettingResponse(
            discord_configured=False,
            discord_enabled=False,
            masked_webhook_url=None,
        )
    return NotificationSettingResponse(
        discord_configured=bool(row.discord_webhook_url),
        discord_enabled=row.discord_enabled,
        masked_webhook_url=mask_webhook_url(decrypt_secret(row.discord_webhook_url)),
    )


@router.patch("", response_model=NotificationSettingResponse)
def update_notification_setting(
    payload: NotificationSettingRequest,
    user_id: int = Query(...),
    db: Session = Depends(get_db),
):
    row = db.query(NotificationSetting).filter(NotificationSetting.user_id == user_id).first()
    if not row:
        row = NotificationSetting(user_id=user_id)
        db.add(row)
    row.discord_webhook_url = encrypt_secret(str(payload.discord_webhook_url)) if payload.discord_webhook_url else None
    row.discord_enabled = payload.discord_enabled
    row.updated_at = utc_now()
    db.commit()
    db.refresh(row)
    return NotificationSettingResponse(
        discord_configured=bool(row.discord_webhook_url),
        discord_enabled=row.discord_enabled,
        masked_webhook_url=mask_webhook_url(decrypt_secret(row.discord_webhook_url)),
    )
