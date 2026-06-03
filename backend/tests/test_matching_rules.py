from app.models import Keyword, Product
from app.services.matching import evaluate_product_match


def make_product(**overrides):
    values = {
        "shop_code": "secondstreet",
        "title": "recolte Grill Pot RRF-3",
        "category": "kitchen",
        "price": 4290,
        "condition_rank": "B",
    }
    values.update(overrides)
    return Product(**values)


def make_keyword(**overrides):
    values = {
        "keyword": "レコルト",
        "shop_code": "all",
        "enabled": True,
        "min_price": None,
        "max_price": None,
        "include_terms": "",
        "exclude_terms": "",
        "allowed_condition_ranks": "",
    }
    values.update(overrides)
    return Keyword(**values)


def test_additional_terms_match_when_main_keyword_does_not():
    decision = evaluate_product_match(
        make_product(title="recolte Grill Pot RRF-3"),
        make_keyword(include_terms="recolte\nRRF"),
    )

    assert decision.base_matched is True
    assert decision.should_notify is True
    assert "recolte" in decision.match_reason


def test_exclude_terms_skip_notification_after_match():
    decision = evaluate_product_match(
        make_product(title="recolte Grill Pot RRF-3 junk"),
        make_keyword(include_terms="recolte", exclude_terms="junk\nジャンク"),
    )

    assert decision.base_matched is True
    assert decision.should_notify is False
    assert decision.skip_reason == "除外語に一致: junk"


def test_price_range_skips_out_of_range_products():
    low = evaluate_product_match(make_product(price=900), make_keyword(include_terms="recolte", min_price=1000))
    high = evaluate_product_match(make_product(price=9000), make_keyword(include_terms="recolte", max_price=8000))

    assert low.should_notify is False
    assert low.skip_reason == "価格が下限未満: 900円 < 1,000円"
    assert high.should_notify is False
    assert high.skip_reason == "価格が上限超過: 9,000円 > 8,000円"


def test_allowed_condition_ranks_filter_products():
    accepted = evaluate_product_match(make_product(condition_rank="B"), make_keyword(include_terms="recolte", allowed_condition_ranks="A,B"))
    rejected = evaluate_product_match(make_product(condition_rank="C"), make_keyword(include_terms="recolte", allowed_condition_ranks="A,B"))
    missing = evaluate_product_match(make_product(condition_rank=None), make_keyword(include_terms="recolte", allowed_condition_ranks="A,B"))

    assert accepted.should_notify is True
    assert rejected.should_notify is False
    assert rejected.skip_reason == "状態ランク対象外: C"
    assert missing.should_notify is False
    assert missing.skip_reason == "状態ランク不明"
