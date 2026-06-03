from dataclasses import dataclass
import gzip
from html import unescape
import re
import unicodedata
from urllib.parse import urljoin
from urllib.request import Request, urlopen
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
    condition_rank: str | None = None
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
    request = Request(url, headers=headers)
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


def normalize_condition_text(value: str | None) -> str:
    if not value:
        return ""
    return unicodedata.normalize("NFKC", strip_tags(value)).upper()


def parse_secondstreet_condition(value: str | None) -> str | None:
    text = normalize_condition_text(value)
    if not text:
        return None
    if "新品" in text:
        return "新品"
    if "未使用" in text:
        return "未使用品"
    match = re.search(r"中古\s*([ABCD])", text)
    if match:
        return f"中古{match.group(1)}"
    return None


def parse_offmall_condition(value: str | None) -> str | None:
    text = normalize_condition_text(value)
    if not text:
        return None
    for rank in ["N", "S", "A", "B", "C", "D"]:
        if re.search(rf"(?:商品ランク|ランク|RANK|状態)\s*[:：]?\s*{rank}\b", text):
            return rank
    return None


def parse_mandarake_condition(value: str | None) -> str | None:
    text = normalize_condition_text(value)
    if not text:
        return None
    match = re.search(r"(?:状態|ランク|RANK|評価)\s*[:：]?\s*(10|[1-9])\b", text)
    if match:
        return match.group(1)
    match = re.search(r"【\s*(10|[1-9])\s*】", text)
    if match:
        return match.group(1)
    return None


def parse_surugaya_condition(value: str | None) -> str | None:
    text = normalize_condition_text(value)
    if not text:
        return "通常中古"
    tags: list[str] = []
    if "ジャンク" in text or "ノークレーム" in text or "ノーリターン" in text:
        tags.append("ジャンク")
    if (
        "破損" in text
        or "ワケあり" in text
        or "訳あり" in text
        or "難あり" in text
        or "状態難" in text
        or "ランクB" in text
    ):
        tags.append("注意あり")
    if "未開封" in text:
        tags.append("未開封品")
    if "帯付き" in text or "帯付" in text:
        tags.append("帯付き")
    if "美品" in text:
        tags.append("美品")
    if not tags:
        tags.append("通常中古")
    return ",".join(dict.fromkeys(tags))


def parse_condition_rank(value: str | None) -> str | None:
    return (
        parse_secondstreet_condition(value)
        or parse_offmall_condition(value)
        or parse_mandarake_condition(value)
        or parse_surugaya_condition(value)
    )


def absolutize(base_url: str, href: str) -> str:
    return urljoin(base_url, unescape(href))
