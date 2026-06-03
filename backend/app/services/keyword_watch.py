from sqlalchemy.orm import Session

from app.models import Keyword
from app.services.shop_crawler import SHOP_FETCHERS, run_shop_crawler


def run_registered_keyword_watch(db: Session, user_id: int, limit: int = 20) -> dict:
    keywords = (
        db.query(Keyword)
        .filter(Keyword.user_id == user_id, Keyword.enabled.is_(True))
        .order_by(Keyword.id.asc())
        .all()
    )
    normalized_limit = max(1, min(50, limit))
    run_count = 0
    skipped_count = 0
    results = []
    seen_pairs: set[tuple[str, str]] = set()

    for keyword in keywords:
        target_shops = _target_shops_for_keyword(keyword.shop_code)
        if not target_shops:
            skipped_count += 1
            continue

        for shop_code in target_shops:
            pair = (shop_code, keyword.keyword)
            if pair in seen_pairs:
                skipped_count += 1
                continue
            seen_pairs.add(pair)

            result = run_shop_crawler(
                db,
                user_id=user_id,
                shop_code=shop_code,
                keyword=keyword.keyword,
                limit=normalized_limit,
            )
            results.append({"shop_code": shop_code, "keyword": keyword.keyword, "result": result})
            run_count += 1

    return {
        "run_count": run_count,
        "skipped_count": skipped_count,
        "results": results,
    }


def _target_shops_for_keyword(shop_code: str) -> list[str]:
    if shop_code == "all":
        return list(SHOP_FETCHERS.keys())
    if shop_code in SHOP_FETCHERS:
        return [shop_code]
    return []
