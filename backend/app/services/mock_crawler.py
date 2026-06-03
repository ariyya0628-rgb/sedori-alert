from sqlalchemy.orm import Session

from app.models import CrawlLog, Keyword, Notification, Product
from app.services.matching import product_matches_keyword
from app.time_utils import utc_now


MOCK_PRODUCTS = [
    {
        "shop_code": "secondstreet",
        "external_product_id": "mock-recolte-001",
        "title": "レコルト ホットプレート",
        "price": 4290,
        "product_url": "https://example.com/secondstreet/mock-recolte-001",
        "image_url": "https://example.com/images/recolte.jpg",
        "category": "生活家電",
    },
    {
        "shop_code": "offmall",
        "external_product_id": "mock-bose-001",
        "title": "Bose QuietComfort Headphones",
        "price": 16800,
        "product_url": "https://example.com/offmall/mock-bose-001",
        "image_url": "https://example.com/images/bose.jpg",
        "category": "オーディオ",
    },
    {
        "shop_code": "surugaya",
        "external_product_id": "mock-switch-001",
        "title": "Nintendo Switch Lite ターコイズ",
        "price": 12980,
        "product_url": "https://example.com/surugaya/mock-switch-001",
        "image_url": "https://example.com/images/switch.jpg",
        "category": "ゲーム",
    },
]


def upsert_mock_product(db: Session, item: dict) -> Product:
    unique_key = f"{item['shop_code']}:{item['external_product_id']}"
    product = db.query(Product).filter(Product.unique_key == unique_key).first()
    if product:
        return product

    product = Product(
        shop_code=item["shop_code"],
        external_product_id=item["external_product_id"],
        unique_key=unique_key,
        title=item["title"],
        price=item["price"],
        product_url=item["product_url"],
        image_url=item["image_url"],
        category=item["category"],
        stock_status="instock",
    )
    db.add(product)
    db.flush()
    return product


def notification_exists(db: Session, user_id: int, product: Product, keyword: Keyword) -> bool:
    return (
        db.query(Notification)
        .filter(
            Notification.user_id == user_id,
            Notification.product_url == product.product_url,
            Notification.matched_keyword == keyword.keyword,
            Notification.discord_status != "skipped",
        )
        .first()
        is not None
    )


def run_mock_crawler(db: Session, user_id: int) -> dict:
    started_at = utc_now()
    fetched_count = len(MOCK_PRODUCTS)
    matched_count = 0
    notifications_created = 0
    duplicates_skipped = 0

    keywords = db.query(Keyword).filter(Keyword.user_id == user_id, Keyword.enabled.is_(True)).all()

    for item in MOCK_PRODUCTS:
        product = upsert_mock_product(db, item)
        for keyword in keywords:
            if not product_matches_keyword(product, keyword):
                continue
            matched_count += 1
            if notification_exists(db, user_id, product, keyword):
                duplicates_skipped += 1
                continue

            db.add(
                Notification(
                    user_id=user_id,
                    shop_code=product.shop_code,
                    product_title=product.title,
                    product_url=product.product_url,
                    matched_keyword=keyword.keyword,
                    discord_status="mock",
                    discord_error=None,
                )
            )
            notifications_created += 1

    db.add(
        CrawlLog(
            shop_code="mock",
            status="success",
            fetched_count=fetched_count,
            matched_count=matched_count,
            notified_count=notifications_created,
            duplicates_skipped=duplicates_skipped,
            started_at=started_at,
            finished_at=utc_now(),
        )
    )
    db.commit()

    return {
        "fetched_count": fetched_count,
        "matched_count": matched_count,
        "notifications_created": notifications_created,
        "duplicates_skipped": duplicates_skipped,
    }
