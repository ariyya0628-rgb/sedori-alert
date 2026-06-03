import re
import os
import subprocess
import tempfile
from pathlib import Path
from urllib.parse import quote
from urllib.error import HTTPError

from app.services.adapters.base import ScrapedProduct, absolutize, fetch_html, parse_price, parse_secondstreet_condition, strip_tags


BASE_URL = "https://www.2ndstreet.jp"
CHROME_PATHS = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
]


def build_secondstreet_search_url(keyword: str) -> str:
    return f"{BASE_URL}/search?keyword={quote(keyword)}"


def find_browser_executable() -> str:
    configured_path = os.environ.get("SEDORI_BROWSER_PATH")
    if configured_path and Path(configured_path).exists():
        return configured_path
    for path in CHROME_PATHS:
        if Path(path).exists():
            return path
    raise RuntimeError("Chrome or Edge was not found for SecondStreet browser fetching")


def fetch_secondstreet_html_with_browser(url: str, timeout: int = 35) -> str:
    browser = find_browser_executable()
    user_agent = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    )
    with tempfile.TemporaryDirectory(prefix="sedori-secondstreet-") as user_data_dir:
        result = subprocess.run(
            [
                browser,
                "--headless=new",
                "--disable-gpu",
                "--disable-extensions",
                "--disable-background-networking",
                "--no-first-run",
                "--no-default-browser-check",
                f"--user-data-dir={user_data_dir}",
                f"--user-agent={user_agent}",
                "--dump-dom",
                url,
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            check=False,
        )
    html = result.stdout.strip()
    if result.returncode != 0 and not html:
        raise RuntimeError((result.stderr or "SecondStreet browser fetch failed").strip())
    if not html:
        raise RuntimeError("SecondStreet browser fetch returned empty HTML")
    return html


def fetch_secondstreet_products(keyword: str, limit: int = 20) -> list[ScrapedProduct]:
    url = build_secondstreet_search_url(keyword)
    try:
        html = fetch_html(url, referer=BASE_URL)
    except HTTPError as exc:
        if exc.code != 403:
            raise
        html = fetch_secondstreet_html_with_browser(url)
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
                condition_rank=parse_secondstreet_condition(text),
            )
        )
        seen_product_ids.add(product_id)
        if len(products) >= limit:
            break
    return products
