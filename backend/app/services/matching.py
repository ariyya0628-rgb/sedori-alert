from dataclasses import dataclass
import re
import unicodedata

from app.models import Keyword, Product


@dataclass(frozen=True)
class MatchDecision:
    base_matched: bool
    should_notify: bool
    match_reason: str | None = None
    skip_reason: str | None = None


def normalize_text(value: str) -> str:
    return unicodedata.normalize("NFKC", value).casefold().strip()


def split_terms(value: str | None) -> list[str]:
    if not value:
        return []
    return [term.strip() for term in re.split(r"[\n,、]+", value) if term.strip()]


def format_price(value: int) -> str:
    return f"{value:,}円"


def normalize_condition(value: str | None) -> str | None:
    if not value:
        return None
    return unicodedata.normalize("NFKC", value).strip().upper()


def keyword_applies_to_shop(keyword: Keyword, shop_code: str) -> bool:
    return keyword.shop_code == "all" or keyword.shop_code == shop_code


def product_text(product: Product) -> str:
    return normalize_text(" ".join(filter(None, [product.title, product.category or "", product.condition_rank or ""])))


def match_terms(product: Product, keyword: Keyword) -> tuple[bool, str | None]:
    haystack = product_text(product)
    terms = [keyword.keyword, *split_terms(keyword.include_terms)]
    for term in terms:
        cleaned = normalize_text(term)
        if cleaned and cleaned in haystack:
            return True, f"一致語: {term}"
    return False, None


def find_exclude_term(product: Product, keyword: Keyword) -> str | None:
    haystack = product_text(product)
    for term in split_terms(keyword.exclude_terms):
        if normalize_text(term) in haystack:
            return term
    return None


def condition_filter_for_shop(keyword: Keyword, shop_code: str) -> tuple[str, str]:
    if shop_code == "secondstreet":
        return "セカスト", keyword.secondstreet_condition_ranks or keyword.allowed_condition_ranks
    if shop_code == "offmall":
        return "オフモール", keyword.offmall_condition_ranks
    if shop_code == "mandarake":
        return "まんだらけ", keyword.mandarake_condition_ranks
    if shop_code == "surugaya":
        return "駿河屋", keyword.surugaya_condition_tags
    return "", ""


def condition_is_allowed(product: Product, keyword: Keyword) -> str | None:
    shop_label, allowed_value = condition_filter_for_shop(keyword, product.shop_code)
    allowed = {normalize_condition(term) for term in split_terms(allowed_value)}
    allowed.discard(None)
    if not allowed:
        return None

    product_conditions = {normalize_condition(term) for term in split_terms(product.condition_rank)}
    product_conditions.discard(None)
    if not product_conditions:
        return f"{shop_label}状態不明"

    if product_conditions & allowed:
        return None

    return f"{shop_label}状態対象外: {product.condition_rank}"


def evaluate_product_match(product: Product, keyword: Keyword) -> MatchDecision:
    if not keyword.enabled or not keyword_applies_to_shop(keyword, product.shop_code):
        return MatchDecision(base_matched=False, should_notify=False)

    base_matched, match_reason = match_terms(product, keyword)
    if not base_matched:
        return MatchDecision(base_matched=False, should_notify=False)

    excluded = find_exclude_term(product, keyword)
    if excluded:
        return MatchDecision(
            base_matched=True,
            should_notify=False,
            match_reason=match_reason,
            skip_reason=f"除外語に一致: {excluded}",
        )

    if keyword.min_price is not None and product.price < keyword.min_price:
        return MatchDecision(
            base_matched=True,
            should_notify=False,
            match_reason=match_reason,
            skip_reason=f"価格が下限未満: {format_price(product.price)} < {format_price(keyword.min_price)}",
        )

    if keyword.max_price is not None and product.price > keyword.max_price:
        return MatchDecision(
            base_matched=True,
            should_notify=False,
            match_reason=match_reason,
            skip_reason=f"価格が上限超過: {format_price(product.price)} > {format_price(keyword.max_price)}",
        )

    condition_skip_reason = condition_is_allowed(product, keyword)
    if condition_skip_reason:
        return MatchDecision(
            base_matched=True,
            should_notify=False,
            match_reason=match_reason,
            skip_reason=condition_skip_reason,
        )

    return MatchDecision(base_matched=True, should_notify=True, match_reason=match_reason)


def product_matches_keyword(product: Product, keyword: Keyword) -> bool:
    return evaluate_product_match(product, keyword).should_notify
