import argparse
import json
import time

from app.services.shop_crawler import SHOP_FETCHERS


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check shop fetchers once.")
    parser.add_argument("--keyword", default="レコルト")
    parser.add_argument("--limit", type=int, default=3)
    args = parser.parse_args(argv)

    normalized_limit = max(1, min(50, args.limit))
    results = []
    for shop_code, fetcher in SHOP_FETCHERS.items():
        started = time.perf_counter()
        try:
            products = fetcher(args.keyword, normalized_limit)
            results.append(
                {
                    "shop_code": shop_code,
                    "status": "success",
                    "count": len(products),
                    "sample_titles": [product.title for product in products[:3]],
                    "error": None,
                    "elapsed_ms": int((time.perf_counter() - started) * 1000),
                }
            )
        except Exception as exc:
            results.append(
                {
                    "shop_code": shop_code,
                    "status": "failed",
                    "count": 0,
                    "sample_titles": [],
                    "error": str(exc),
                    "elapsed_ms": int((time.perf_counter() - started) * 1000),
                }
            )

    print(
        json.dumps(
            {
                "keyword": args.keyword,
                "limit": normalized_limit,
                "results": results,
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
