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


def normalize_rank(value: str | None) -> str | None:
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

    allowed_ranks = {normalize_rank(rank) for rank in split_terms(keyword.allowed_condition_ranks)}
    allowed_ranks.discard(None)
    if allowed_ranks:
        product_rank = normalize_rank(product.condition_rank)
        if not product_rank:
            return MatchDecision(
                base_matched=True,
                should_notify=False,
                match_reason=match_reason,
                skip_reason="状態ランク不明",
            )
        if product_rank not in allowed_ranks:
            return MatchDecision(
                base_matched=True,
                should_notify=False,
                match_reason=match_reason,
                skip_reason=f"状態ランク対象外: {product.condition_rank}",
            )

    return MatchDecision(base_matched=True, should_notify=True, match_reason=match_reason)


def product_matches_keyword(product: Product, keyword: Keyword) -> bool:
    return evaluate_product_match(product, keyword).should_notify
