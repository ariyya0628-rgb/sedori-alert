import argparse
import json
import sys

from app.database import SessionLocal
from app.services.scheduler import run_due_scheduler


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run due scheduler settings once.")
    parser.add_argument("--user-id", type=int, default=1)
    args = parser.parse_args(argv)

    try:
        with SessionLocal() as db:
            result = run_due_scheduler(db, args.user_id)
        print(json.dumps(result, ensure_ascii=False, default=str))
        return 0
    except Exception as exc:
        error = {"ran": False, "reason": "scheduler error", "error": str(exc)}
        print(json.dumps(error, ensure_ascii=False), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
