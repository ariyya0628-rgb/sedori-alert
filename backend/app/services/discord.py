import httpx

from app.services.adapters.base import ScrapedProduct


def mask_webhook_url(url: str | None) -> str | None:
    if not url:
        return None
    if len(url) <= 16:
        return "********"
    return f"{url[:20]}...{url[-5:]}"


def build_product_notification_payload(product: ScrapedProduct, keyword_text: str) -> dict:
    fields = [
        {"name": "ショップ", "value": product.shop_code, "inline": True},
        {"name": "キーワード", "value": keyword_text, "inline": True},
        {"name": "価格", "value": f"{product.price:,}円" if product.price else "-", "inline": True},
    ]
    if product.category:
        fields.append({"name": "カテゴリ", "value": product.category, "inline": True})

    embed = {
        "title": product.title,
        "url": product.product_url,
        "color": 0x2F80ED,
        "fields": fields,
        "footer": {"text": "Sedori Alert"},
    }
    if product.image_url:
        embed["image"] = {"url": product.image_url}

    return {
        "content": "新着商品を検知しました",
        "embeds": [embed],
    }


async def send_discord_webhook(webhook_url: str, content: str | None = None, payload: dict | None = None) -> tuple[bool, str | None]:
    try:
        body = payload or {"content": content or ""}
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(webhook_url, json=body)
        if response.status_code in (200, 204):
            return True, None
        return False, f"Discord returned HTTP {response.status_code}"
    except Exception as exc:
        return False, str(exc)


async def send_discord_product_notification(
    webhook_url: str,
    product: ScrapedProduct,
    keyword_text: str,
) -> tuple[bool, str | None]:
    return await send_discord_webhook(
        webhook_url,
        payload=build_product_notification_payload(product, keyword_text),
    )
