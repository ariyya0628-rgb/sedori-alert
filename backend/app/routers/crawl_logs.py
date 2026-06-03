from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import CrawlLog
from app.schemas import CrawlLogResponse


router = APIRouter(prefix="/api/crawl-logs", tags=["crawl-logs"])


@router.get("", response_model=list[CrawlLogResponse])
def list_crawl_logs(db: Session = Depends(get_db)):
    return db.query(CrawlLog).order_by(CrawlLog.finished_at.desc()).all()
