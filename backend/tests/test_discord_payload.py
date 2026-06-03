from app.services.adapters.base import ScrapedProduct
from app.services.discord import build_product_notification_payload


def test_build_product_notification_payload_uses_embed_fields_and_image():
    product = ScrapedProduct(
        shop_code="surugaya",
        external_product_id="123",
        title="レコルト カプセルカッター ボンヌ",
        price=3980,
        product_url="https://example.com/item/123",
        image_url="https://example.com/item/123.jpg",
        category="家電",
    )

    payload = build_product_notification_payload(product, "レコルト")

    assert payload["content"] == "新着商品を検知しました"
    embed = payload["embeds"][0]
    assert embed["title"] == "レコルト カプセルカッター ボンヌ"
    assert embed["url"] == "https://example.com/item/123"
    assert embed["fields"] == [
        {"name": "ショップ", "value": "surugaya", "inline": True},
        {"name": "キーワード", "value": "レコルト", "inline": True},
        {"name": "価格", "value": "3,980円", "inline": True},
        {"name": "カテゴリ", "value": "家電", "inline": True},
    ]
    assert embed["image"] == {"url": "https://example.com/item/123.jpg"}


def test_build_product_notification_payload_without_optional_values():
    product = ScrapedProduct(
        shop_code="offmall",
        external_product_id="456",
        title="価格未設定の商品",
        price=0,
        product_url="https://example.com/item/456",
    )

    payload = build_product_notification_payload(product, "未設定")

    embed = payload["embeds"][0]
    assert {"name": "価格", "value": "-", "inline": True} in embed["fields"]
    assert "image" not in embed
