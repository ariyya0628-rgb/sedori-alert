import unicodedata

from app.models import Keyword, Product


def normalize_text(value: str) -> str:
    return unicodedata.normalize("NFKC", value).casefold().strip()


def keyword_applies_to_shop(keyword: Keyword, shop_code: str) -> bool:
    return keyword.shop_code == "all" or keyword.shop_code == shop_code


def product_matches_keyword(product: Product, keyword: Keyword) -> bool:
    if not keyword.enabled or not keyword_applies_to_shop(keyword, product.shop_code):
        return False
    haystack = normalize_text(" ".join(filter(None, [product.title, product.category or ""])))
    needle = normalize_text(keyword.keyword)
    return bool(needle and needle in haystack)
