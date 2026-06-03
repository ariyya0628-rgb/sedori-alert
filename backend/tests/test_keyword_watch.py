from uuid import uuid4

from fastapi.testclient import TestClient

from app.database import SessionLocal
from app.main import app


client = TestClient(app)


def unique_user_id() -> int:
    return int(str(uuid4().int)[:8])


def test_registered_keyword_watch_runs_enabled_keywords_for_target_shops(monkeypatch):
    from app.services.keyword_watch import run_registered_keyword_watch

    user_id = unique_user_id()
    calls: list[tuple[int, str, str, int]] = []

    def fake_run_shop_crawler(db, user_id: int, shop_code: str, keyword: str, limit: int):
        calls.append((user_id, shop_code, keyword, limit))
        return {
            "fetched_count": 1,
            "matched_count": 1,
            "notifications_created": 1,
            "duplicates_skipped": 0,
            "status": "success",
            "error_message": None,
        }

    monkeypatch.setattr(
        "app.services.keyword_watch.SHOP_FETCHERS",
        {"offmall": object(), "surugaya": object()},
    )
    monkeypatch.setattr("app.services.keyword_watch.run_shop_crawler", fake_run_shop_crawler)

    client.post("/api/keywords", json={"user_id": user_id, "keyword": "レコルト", "shop_code": "all"})
    client.post("/api/keywords", json={"user_id": user_id, "keyword": "ゲーム", "shop_code": "surugaya"})
    client.post("/api/keywords", json={"user_id": user_id, "keyword": "未対応", "shop_code": "unknown"})

    with SessionLocal() as db:
        result = run_registered_keyword_watch(db, user_id=user_id, limit=3)

    assert result["run_count"] == 3
    assert result["skipped_count"] == 1
    assert calls == [
        (user_id, "offmall", "レコルト", 3),
        (user_id, "surugaya", "レコルト", 3),
        (user_id, "surugaya", "ゲーム", 3),
    ]


def test_run_registered_keywords_api(monkeypatch):
    user_id = unique_user_id()

    def fake_watch(db, user_id: int, limit: int):
        return {"run_count": 2, "skipped_count": 0, "results": []}

    monkeypatch.setattr("app.routers.crawler.run_registered_keyword_watch", fake_watch)

    response = client.post(f"/api/crawler/run-keywords?user_id={user_id}&limit=5")

    assert response.status_code == 200
    assert response.json()["run_count"] == 2
