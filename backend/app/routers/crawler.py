from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import MockCrawlerRunResponse, ShopCrawlerRunResponse
from app.services.mock_crawler import run_mock_crawler
from app.services.shop_crawler import SHOP_FETCHERS, run_shop_crawler


router = APIRouter(prefix="/api/crawler", tags=["crawler"])


@router.post("/run-mock", response_model=MockCrawlerRunResponse)
def run_mock(user_id: int = Query(...), db: Session = Depends(get_db)):
    return run_mock_crawler(db, user_id)


@router.post("/run-shop", response_model=ShopCrawlerRunResponse)
def run_shop(
    user_id: int = Query(...),
    shop_code: str = Query(...),
    keyword: str = Query(...),
    limit: int = Query(20, ge=1, le=50),
    db: Session = Depends(get_db),
):
    if shop_code not in SHOP_FETCHERS:
        raise HTTPException(status_code=400, detail="Unsupported shop_code")
    return run_shop_crawler(db, user_id=user_id, shop_code=shop_code, keyword=keyword, limit=limit)
