from datetime import timedelta

from sqlalchemy.orm import Session

from app.models import SchedulerSetting
from app.services.shop_crawler import run_shop_crawler
from app.time_utils import utc_now


def get_or_create_scheduler_setting(db: Session, user_id: int) -> SchedulerSetting:
    row = db.query(SchedulerSetting).filter(SchedulerSetting.user_id == user_id).first()
    if row:
        return row
    row = SchedulerSetting(user_id=user_id, enabled=False, shop_code="offmall", keyword="", interval_minutes=10, limit=10)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def update_scheduler_setting(
    db: Session,
    user_id: int,
    enabled: bool,
    shop_code: str,
    keyword: str,
    interval_minutes: int,
    limit: int,
) -> SchedulerSetting:
    row = get_or_create_scheduler_setting(db, user_id)
    row.enabled = enabled
    row.shop_code = shop_code
    row.keyword = keyword.strip()
    row.interval_minutes = max(1, interval_minutes)
    row.limit = max(1, min(50, limit))
    row.next_run_at = utc_now() if enabled else None
    row.updated_at = utc_now()
    db.commit()
    db.refresh(row)
    return row


def run_due_scheduler(db: Session, user_id: int) -> dict:
    row = get_or_create_scheduler_setting(db, user_id)
    if not row.enabled:
        return {"ran": False, "reason": "scheduler disabled", "result": None}
    if not row.keyword:
        return {"ran": False, "reason": "keyword is empty", "result": None}

    now = utc_now()
    if row.next_run_at and row.next_run_at > now:
        return {"ran": False, "reason": "not due yet", "result": None}

    result = run_shop_crawler(db, user_id=user_id, shop_code=row.shop_code, keyword=row.keyword, limit=row.limit)
    row.last_run_at = now
    row.next_run_at = now + timedelta(minutes=row.interval_minutes)
    row.updated_at = now
    db.commit()
    return {"ran": True, "reason": None, "result": result}
