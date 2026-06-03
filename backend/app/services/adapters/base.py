from dataclasses import dataclass
from html import unescape
from urllib.parse import urljoin
from urllib.request import Request, urlopen
import re


@dataclass(frozen=True)
class ScrapedProduct:
    shop_code: str
    external_product_id: str
    title: str
    price: int
    product_url: str
    image_url: str | None = None
    category: str | None = None
    stock_status: str = "instock"


def fetch_html(url: str, timeout: int = 20) -> str:
    request = Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept-Language": "ja,en-US;q=0.9,en;q=0.8",
        },
    )
    with urlopen(request, timeout=timeout) as response:
        return response.read().decode("utf-8", "replace")


def strip_tags(value: str) -> str:
    text = re.sub(r"<[^>]+>", " ", value)
    return re.sub(r"\s+", " ", unescape(text)).strip()


def extract_first(pattern: str, value: str) -> str | None:
    match = re.search(pattern, value, re.IGNORECASE | re.DOTALL)
    return unescape(match.group(1)).strip() if match else None


def parse_price(value: str | None) -> int:
    if not value:
        return 0
    digits = re.sub(r"[^\d]", "", value)
    return int(digits) if digits else 0


def absolutize(base_url: str, href: str) -> str:
    return urljoin(base_url, unescape(href))
