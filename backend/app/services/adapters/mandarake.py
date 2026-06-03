from urllib.parse import quote
import re

from app.services.adapters.base import (
    ScrapedProduct,
    absolutize,
    extract_first,
    fetch_html,
    parse_price,
    strip_tags,
)


BASE_URL = "https://order.mandarake.co.jp"


def build_mandarake_search_url(keyword: str) -> str:
    return (
        f"{BASE_URL}/order/listPage/list?"
        f"keyword={quote(keyword)}&soldOut=0&dispAdult=0&lang=ja"
    )


def fetch_mandarake_products(keyword: str, limit: int = 20) -> list[ScrapedProduct]:
    html = fetch_html(build_mandarake_search_url(keyword))
    return parse_mandarake_products(html, limit=limit)


def parse_mandarake_products(html: str, limit: int = 20) -> list[ScrapedProduct]:
    products: list[ScrapedProduct] = []
    anchors = re.findall(
        r'<a[^>]+href="([^"]*/order/detailPage/item\?[^"]*itemCode=(\d+)[^"]*)"[^>]*>(.*?)</a>',
        html,
        re.IGNORECASE | re.DOTALL,
    )

    for href, product_id, body in anchors:
        title = strip_tags(extract_first(r'class="[^"]*(?:item-title|title)[^"]*"[^>]*>(.*?)</', body) or "")
        if not title:
            title = strip_tags(extract_first(r'alt="([^"]+)"', body) or "")
        if not title:
            title = strip_tags(body)
        if not title:
            continue

        price_match = re.search(r"(?:¥|￥)?\s*[\d,]+\s*円", body)
        image_url = extract_first(r'<img[^>]+src="([^"]+)"', body)

        products.append(
            ScrapedProduct(
                shop_code="mandarake",
                external_product_id=product_id,
                title=title,
                price=parse_price(price_match.group(0) if price_match else None),
                product_url=absolutize(BASE_URL, href),
                image_url=absolutize(BASE_URL, image_url) if image_url else None,
                category=None,
            )
        )
        if len(products) >= limit:
            break

    return products
