import re
from urllib.parse import quote

from app.services.adapters.base import ScrapedProduct, absolutize, fetch_html, parse_price, strip_tags


BASE_URL = "https://www.2ndstreet.jp"


def build_secondstreet_search_url(keyword: str) -> str:
    return f"{BASE_URL}/search?keyword={quote(keyword)}"


def fetch_secondstreet_products(keyword: str, limit: int = 20) -> list[ScrapedProduct]:
    html = fetch_html(build_secondstreet_search_url(keyword), referer=BASE_URL)
    return parse_secondstreet_products(html, limit=limit)


def clean_secondstreet_title(text: str, price_text: str | None) -> str:
    title = re.sub(r"商品の状態\s*:\s*.*$", "", text).strip()
    if price_text:
        title = title.replace(price_text, "").strip()
    return title or text


def parse_secondstreet_products(html: str, limit: int = 20) -> list[ScrapedProduct]:
    products: list[ScrapedProduct] = []
    seen_product_ids: set[str] = set()
    anchors = re.findall(
        r"<a[^>]+href=[\"']([^\"']*/goods/detail/goodsId/([^/\"']+)[^\"']*)[\"'][^>]*>(.*?)</a>",
        html,
        re.IGNORECASE | re.DOTALL,
    )
    for href, product_id, body in anchors:
        if product_id in seen_product_ids:
            continue
        text = strip_tags(body)
        if not text:
            continue
        price_match = re.search(r"(?:￥|¥|ﾂ･)\s*[\d,]+", text)
        price_text = price_match.group(0) if price_match else None
        products.append(
            ScrapedProduct(
                shop_code="secondstreet",
                external_product_id=product_id,
                title=clean_secondstreet_title(text, price_text),
                price=parse_price(price_text),
                product_url=absolutize(BASE_URL, href),
                image_url=None,
                category=None,
            )
        )
        seen_product_ids.add(product_id)
        if len(products) >= limit:
            break
    return products
