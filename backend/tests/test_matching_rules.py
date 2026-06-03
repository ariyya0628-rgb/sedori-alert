from app.models import Keyword, Product
from app.services.matching import evaluate_product_match


def make_product(**overrides):
    values = {
        "shop_code": "secondstreet",
        "title": "recolte Grill Pot RRF-3",
        "category": "kitchen",
        "price": 4290,
        "condition_rank": "中古B",
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
        "secondstreet_condition_ranks": "",
        "offmall_condition_ranks": "",
        "mandarake_condition_ranks": "",
        "surugaya_condition_tags": "",
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
    assert decision.match_reason == "一致語: recolte"


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


def test_secondstreet_condition_uses_secondstreet_rank_list_only():
    accepted = evaluate_product_match(
        make_product(shop_code="secondstreet", condition_rank="中古B"),
        make_keyword(include_terms="recolte", secondstreet_condition_ranks="新品,未使用品,中古A,中古B"),
    )
    rejected = evaluate_product_match(
        make_product(shop_code="secondstreet", condition_rank="中古C"),
        make_keyword(include_terms="recolte", secondstreet_condition_ranks="新品,未使用品,中古A,中古B"),
    )

    assert accepted.should_notify is True
    assert rejected.should_notify is False
    assert rejected.skip_reason == "セカスト状態対象外: 中古C"


def test_offmall_condition_uses_offmall_rank_list_only():
    accepted = evaluate_product_match(
        make_product(shop_code="offmall", condition_rank="B"),
        make_keyword(include_terms="recolte", offmall_condition_ranks="N,S,A,B"),
    )
    rejected = evaluate_product_match(
        make_product(shop_code="offmall", condition_rank="C"),
        make_keyword(include_terms="recolte", offmall_condition_ranks="N,S,A,B"),
    )

    assert accepted.should_notify is True
    assert rejected.should_notify is False
    assert rejected.skip_reason == "オフモール状態対象外: C"


def test_mandarake_condition_uses_numeric_rank_list():
    accepted = evaluate_product_match(
        make_product(shop_code="mandarake", condition_rank="8"),
        make_keyword(include_terms="recolte", mandarake_condition_ranks="10,9,8,7"),
    )
    rejected = evaluate_product_match(
        make_product(shop_code="mandarake", condition_rank="5"),
        make_keyword(include_terms="recolte", mandarake_condition_ranks="10,9,8,7"),
    )

    assert accepted.should_notify is True
    assert rejected.should_notify is False
    assert rejected.skip_reason == "まんだらけ状態対象外: 5"


def test_surugaya_condition_uses_condition_tags():
    accepted = evaluate_product_match(
        make_product(shop_code="surugaya", condition_rank="未開封品,美品"),
        make_keyword(include_terms="recolte", surugaya_condition_tags="未開封品,美品,通常中古"),
    )
    rejected = evaluate_product_match(
        make_product(shop_code="surugaya", condition_rank="ジャンク"),
        make_keyword(include_terms="recolte", surugaya_condition_tags="未開封品,美品,通常中古"),
    )

    assert accepted.should_notify is True
    assert rejected.should_notify is False
    assert rejected.skip_reason == "駿河屋状態対象外: ジャンク"
