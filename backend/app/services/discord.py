import httpx


def mask_webhook_url(url: str | None) -> str | None:
    if not url:
        return None
    if len(url) <= 16:
        return "********"
    return f"{url[:20]}...{url[-5:]}"


async def send_discord_webhook(webhook_url: str, content: str) -> tuple[bool, str | None]:
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(webhook_url, json={"content": content})
        if response.status_code in (200, 204):
            return True, None
        return False, f"Discord returned HTTP {response.status_code}"
    except Exception as exc:
        return False, str(exc)
