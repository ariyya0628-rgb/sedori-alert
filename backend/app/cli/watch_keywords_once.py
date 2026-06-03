import argparse
import json
import sys

from app.database import SessionLocal
from app.services.keyword_watch import run_registered_keyword_watch


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run registered keyword watch once.")
    parser.add_argument("--user-id", type=int, default=1)
    parser.add_argument("--limit", type=int, default=20)
    args = parser.parse_args(argv)

    try:
        with SessionLocal() as db:
            result = run_registered_keyword_watch(db, user_id=args.user_id, limit=args.limit)
        print(json.dumps(result, ensure_ascii=False, default=str))
        return 0
    except Exception as exc:
        error = {"run_count": 0, "skipped_count": 0, "results": [], "error": str(exc)}
        print(json.dumps(error, ensure_ascii=False), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
