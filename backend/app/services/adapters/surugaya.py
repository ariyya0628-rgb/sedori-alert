from urllib.parse import quote
import re

from app.services.adapters.base import (
    ScrapedProduct,
    absolutize,
    extract_first,
    fetch_html,
    parse_price,
    parse_surugaya_condition,
    strip_tags,
)


BASE_URL = "https://www.suruga-ya.jp"


def build_surugaya_search_url(keyword: str) -> str:
    return f"{BASE_URL}/search?search_word={quote(keyword)}"


def fetch_surugaya_products(keyword: str, limit: int = 20) -> list[ScrapedProduct]:
    html = fetch_html(build_surugaya_search_url(keyword))
    return parse_surugaya_products(html, limit=limit)


def parse_surugaya_products(html: str, limit: int = 20) -> list[ScrapedProduct]:
    products: list[ScrapedProduct] = []
    anchors = re.findall(
        r'<a[^>]+href="([^"]*/product/detail/([^/?#"]+)[^"]*)"[^>]*>(.*?)</a>',
        html,
        re.IGNORECASE | re.DOTALL,
    )

    seen_ids: set[str] = set()
    for href, product_id, body in anchors:
        if product_id in seen_ids:
            continue
        seen_ids.add(product_id)

        block = _extract_surugaya_block(html, href, body)
        title = strip_tags(body)
        if not title:
            title = strip_tags(extract_first(r'alt="([^"]+)"', block) or "")
        if not title:
            continue

        price_match = re.search(r"(?:¥|￥)?\s*[\d,]+\s*円", block)
        image_url = extract_first(r'<img[^>]+(?:data-src|src)="([^"]+)"', block)

        products.append(
            ScrapedProduct(
                shop_code="surugaya",
                external_product_id=product_id,
                title=title,
                price=parse_price(price_match.group(0) if price_match else None),
                product_url=absolutize(BASE_URL, href),
                image_url=absolutize(BASE_URL, image_url) if image_url else None,
                category=None,
                condition_rank=parse_surugaya_condition(f"{title} {block}"),
            )
        )
        if len(products) >= limit:
            break

    return products


def _extract_surugaya_block(html: str, href: str, body: str) -> str:
    href_index = html.find(href)
    if href_index == -1:
        return body

    start_candidates = [
        html.rfind('<div class="item', 0, href_index),
        html.rfind("<li", 0, href_index),
    ]
    start = max(start_candidates)
    if start == -1:
        return body

    next_div = html.find('<div class="item', href_index + len(href))
    next_li = html.find("<li", href_index + len(href))
    end_candidates = [value for value in [next_div, next_li] if value != -1]
    end = min(end_candidates) if end_candidates else len(html)
    return html[start:end]
