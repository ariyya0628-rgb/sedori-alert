from urllib.parse import quote
import re

from app.services.adapters.base import ScrapedProduct, absolutize, fetch_html, parse_price, strip_tags


BASE_URL = "https://www.2ndstreet.jp"


def build_secondstreet_search_url(keyword: str) -> str:
    return f"{BASE_URL}/search?keyword={quote(keyword)}"


def fetch_secondstreet_products(keyword: str, limit: int = 20) -> list[ScrapedProduct]:
    html = fetch_html(build_secondstreet_search_url(keyword))
    return parse_secondstreet_products(html, limit=limit)


def parse_secondstreet_products(html: str, limit: int = 20) -> list[ScrapedProduct]:
    products: list[ScrapedProduct] = []
    anchors = re.findall(
        r'<a[^>]+href="([^"]*/goods/detail/goodsId/([^/"]+)[^"]*)"[^>]*>(.*?)</a>',
        html,
        re.IGNORECASE | re.DOTALL,
    )
    for href, product_id, body in anchors:
        text = strip_tags(body)
        if not text:
            continue
        price_match = re.search(r"¥\s*[\d,]+", text)
        price = parse_price(price_match.group(0) if price_match else None)
        title = re.sub(r"商品の状態\s*:\s*.*$", "", text).strip()
        if not title:
            title = text
        products.append(
            ScrapedProduct(
                shop_code="secondstreet",
                external_product_id=product_id,
                title=title,
                price=price,
                product_url=absolutize(BASE_URL, href),
                image_url=None,
                category=None,
            )
        )
        if len(products) >= limit:
            break
    return products
