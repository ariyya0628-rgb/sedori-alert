from dataclasses import dataclass
from html import unescape
from urllib.parse import urljoin
from urllib.request import Request, urlopen
import gzip
import re
import zlib


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


def fetch_html(url: str, timeout: int = 20, referer: str | None = None) -> str:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/125.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "ja-JP,ja;q=0.9,en-US;q=0.8,en;q=0.7",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
        "Upgrade-Insecure-Requests": "1",
    }
    if referer:
        headers["Referer"] = referer
    request = Request(
        url,
        headers=headers,
    )
    with urlopen(request, timeout=timeout) as response:
        body = response.read()
        encoding = response.headers.get("Content-Encoding", "").lower()
        if encoding == "gzip":
            body = gzip.decompress(body)
        elif encoding == "deflate":
            body = zlib.decompress(body)
        return body.decode("utf-8", "replace")


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
