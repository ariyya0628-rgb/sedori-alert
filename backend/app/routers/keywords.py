from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Keyword
from app.schemas import KeywordCreate, KeywordResponse, KeywordUpdate


router = APIRouter(prefix="/api/keywords", tags=["keywords"])


class KeywordCreateRequest(KeywordCreate):
    user_id: int


@router.get("", response_model=list[KeywordResponse])
def list_keywords(user_id: int = Query(...), db: Session = Depends(get_db)):
    return (
        db.query(Keyword)
        .filter(Keyword.user_id == user_id)
        .order_by(Keyword.created_at.desc())
        .all()
    )


@router.post("", response_model=KeywordResponse)
def create_keyword(payload: KeywordCreateRequest, db: Session = Depends(get_db)):
    keyword = payload.keyword.strip()
    if not keyword:
        raise HTTPException(status_code=400, detail="Keyword is required")

    existing = (
        db.query(Keyword)
        .filter(
            Keyword.user_id == payload.user_id,
            Keyword.keyword == keyword,
            Keyword.shop_code == payload.shop_code,
        )
        .first()
    )
    if existing:
        return existing

    row = Keyword(user_id=payload.user_id, keyword=keyword, shop_code=payload.shop_code)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@router.patch("/{keyword_id}", response_model=KeywordResponse)
def update_keyword(keyword_id: int, payload: KeywordUpdate, db: Session = Depends(get_db)):
    row = db.query(Keyword).filter(Keyword.id == keyword_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Keyword not found")
    if payload.keyword is not None:
        cleaned = payload.keyword.strip()
        if not cleaned:
            raise HTTPException(status_code=400, detail="Keyword is required")
        row.keyword = cleaned
    if payload.shop_code is not None:
        row.shop_code = payload.shop_code
    if payload.enabled is not None:
        row.enabled = payload.enabled
    db.commit()
    db.refresh(row)
    return row


@router.delete("/{keyword_id}")
def delete_keyword(keyword_id: int, db: Session = Depends(get_db)):
    row = db.query(Keyword).filter(Keyword.id == keyword_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Keyword not found")
    db.delete(row)
    db.commit()
    return {"deleted": True}
