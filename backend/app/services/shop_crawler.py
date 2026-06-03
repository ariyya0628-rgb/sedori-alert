from typing import Callable

from sqlalchemy.orm import Session

from app.models import CrawlLog, Keyword, Notification, Product
from app.services.adapters.base import ScrapedProduct
from app.services.adapters.offmall import fetch_offmall_products
from app.services.adapters.secondstreet import fetch_secondstreet_products
from app.models import NotificationSetting
from app.services.discord import send_discord_webhook
from app.services.secrets import decrypt_secret
from app.services.matching import product_matches_keyword
from app.services.mock_crawler import notification_exists
from app.time_utils import utc_now


SHOP_FETCHERS: dict[str, Callable[[str, int], list[ScrapedProduct]]] = {
    "offmall": fetch_offmall_products,
    "secondstreet": fetch_secondstreet_products,
}


def upsert_scraped_product(db: Session, item: ScrapedProduct) -> Product:
    unique_key = f"{item.shop_code}:{item.external_product_id}"
    product = db.query(Product).filter(Product.unique_key == unique_key).first()
    if product:
        product.title = item.title
        product.price = item.price
        product.product_url = item.product_url
        product.image_url = item.image_url
        product.category = item.category
        product.stock_status = item.stock_status
        return product

    product = Product(
        shop_code=item.shop_code,
        external_product_id=item.external_product_id,
        unique_key=unique_key,
        title=item.title,
        price=item.price,
        product_url=item.product_url,
        image_url=item.image_url,
        category=item.category,
        stock_status=item.stock_status,
    )
    db.add(product)
    db.flush()
    return product


def process_scraped_products(db: Session, user_id: int, scraped_products: list[ScrapedProduct]) -> dict:
    matched_count = 0
    notifications_created = 0
    duplicates_skipped = 0
    keywords = db.query(Keyword).filter(Keyword.user_id == user_id, Keyword.enabled.is_(True)).all()
    notification_setting = (
        db.query(NotificationSetting).filter(NotificationSetting.user_id == user_id).first()
    )

    for scraped in scraped_products:
        product = upsert_scraped_product(db, scraped)
        for keyword in keywords:
            if not product_matches_keyword(product, keyword):
                continue
            matched_count += 1
            if notification_exists(db, user_id, product, keyword):
                duplicates_skipped += 1
                continue
            discord_status = "disabled"
            discord_error = None
            webhook_url = decrypt_secret(notification_setting.discord_webhook_url) if notification_setting else None
            if notification_setting and notification_setting.discord_enabled and webhook_url:
                import asyncio

                content = (
                    f"[{product.shop_code}] 新着商品を検知しました\n"
                    f"キーワード: {keyword.keyword}\n"
                    f"商品名: {product.title}\n"
                    f"価格: {product.price:,}円\n"
                    f"URL: {product.product_url}"
                )
                ok, discord_error = asyncio.run(
                    send_discord_webhook(webhook_url, content)
                )
                discord_status = "success" if ok else "failed"

            db.add(
                Notification(
                    user_id=user_id,
                    shop_code=product.shop_code,
                    product_title=product.title,
                    product_url=product.product_url,
                    matched_keyword=keyword.keyword,
                    discord_status=discord_status,
                    discord_error=discord_error,
                )
            )
            notifications_created += 1

    return {
        "matched_count": matched_count,
        "notifications_created": notifications_created,
        "duplicates_skipped": duplicates_skipped,
    }


def run_shop_crawler(db: Session, user_id: int, shop_code: str, keyword: str, limit: int = 20) -> dict:
    started_at = utc_now()
    fetcher = SHOP_FETCHERS[shop_code]
    fetched_count = 0
    error_message = None
    result = {"matched_count": 0, "notifications_created": 0, "duplicates_skipped": 0}

    try:
        scraped_products = fetcher(keyword, limit)
        fetched_count = len(scraped_products)
        result = process_scraped_products(db, user_id, scraped_products)
        status = "success"
    except Exception as exc:
        status = "failed"
        error_message = str(exc)

    db.add(
        CrawlLog(
            shop_code=shop_code,
            status=status,
            fetched_count=fetched_count,
            matched_count=result["matched_count"],
            notified_count=result["notifications_created"],
            duplicates_skipped=result["duplicates_skipped"],
            error_message=error_message,
            started_at=started_at,
            finished_at=utc_now(),
        )
    )
    db.commit()

    return {
        "fetched_count": fetched_count,
        "matched_count": result["matched_count"],
        "notifications_created": result["notifications_created"],
        "duplicates_skipped": result["duplicates_skipped"],
        "status": status,
        "error_message": error_message,
    }
