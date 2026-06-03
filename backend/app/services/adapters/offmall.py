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


BASE_URL = "https://netmall.hardoff.co.jp"


def build_offmall_search_url(keyword: str) -> str:
    return f"{BASE_URL}/search/?q={quote(keyword)}"


def fetch_offmall_products(keyword: str, limit: int = 20) -> list[ScrapedProduct]:
    html = fetch_html(build_offmall_search_url(keyword))
    return parse_offmall_products(html, limit=limit)


def parse_offmall_products(html: str, limit: int = 20) -> list[ScrapedProduct]:
    products: list[ScrapedProduct] = []
    blocks = re.findall(
        r'<div class="itemcolmn_item[^"]*">(.*?)(?=<div class="itemcolmn_item|\Z)',
        html,
        re.IGNORECASE | re.DOTALL,
    )
    for block in blocks:
        href = extract_first(r'<a[^>]+href="([^"]*/product/(\d+)/[^"]*)"', block)
        product_id_match = re.search(r"/product/(\d+)/", href or "")
        if not href or not product_id_match:
            continue

        brand = strip_tags(extract_first(r'<div class="item-brand-name">(.*?)</div>', block) or "")
        name = strip_tags(extract_first(r'<div class="item-name">(.*?)</div>', block) or "")
        code = strip_tags(extract_first(r'<div class="item-code">(.*?)</div>', block) or "")
        price_text = strip_tags(extract_first(r'<div class="item-price">(.*?)</div>', block) or "")
        image_url = extract_first(r'<img[^>]+src="([^"]+)"', block)
        title = " ".join(part for part in [brand, name, code] if part).strip()
        if not title:
            title = strip_tags(extract_first(r'alt="([^"]+)"', block) or "")

        products.append(
            ScrapedProduct(
                shop_code="offmall",
                external_product_id=product_id_match.group(1),
                title=title,
                price=parse_price(price_text),
                product_url=absolutize(BASE_URL, href),
                image_url=image_url,
                category=None,
            )
        )
        if len(products) >= limit:
            break
    return products
