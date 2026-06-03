from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import SchedulerRunDueResponse, SchedulerSettingRequest, SchedulerSettingResponse
from app.services.scheduler import get_or_create_scheduler_setting, run_due_scheduler, update_scheduler_setting


router = APIRouter(prefix="/api/scheduler", tags=["scheduler"])


@router.get("/settings", response_model=SchedulerSettingResponse)
def get_settings(user_id: int = Query(...), db: Session = Depends(get_db)):
    return get_or_create_scheduler_setting(db, user_id)


@router.put("/settings", response_model=SchedulerSettingResponse)
def put_settings(
    payload: SchedulerSettingRequest,
    user_id: int = Query(...),
    db: Session = Depends(get_db),
):
    return update_scheduler_setting(
        db=db,
        user_id=user_id,
        enabled=payload.enabled,
        shop_code=payload.shop_code,
        keyword=payload.keyword,
        interval_minutes=payload.interval_minutes,
        limit=payload.limit,
    )


@router.post("/run-due", response_model=SchedulerRunDueResponse)
def run_due(user_id: int = Query(...), db: Session = Depends(get_db)):
    return run_due_scheduler(db, user_id)
