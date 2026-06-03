from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.frontend import mount_frontend


def test_mount_frontend_serves_index_and_assets(tmp_path):
    dist = tmp_path / "dist"
    assets = dist / "assets"
    assets.mkdir(parents=True)
    (dist / "index.html").write_text('<div id="root"></div><script src="/assets/app.js"></script>', encoding="utf-8")
    (assets / "app.js").write_text("console.log('ok')", encoding="utf-8")

    app = FastAPI()

    @app.get("/api/example")
    def api_example():
        return {"ok": True}

    mounted = mount_frontend(app, dist)
    client = TestClient(app)

    assert mounted is True
    assert client.get("/").text == '<div id="root"></div><script src="/assets/app.js"></script>'
    assert client.get("/dashboard").text == '<div id="root"></div><script src="/assets/app.js"></script>'
    assert client.get("/assets/app.js").text == "console.log('ok')"
    assert client.get("/api/example").json() == {"ok": True}
    assert client.get("/api/missing").status_code == 404


def test_mount_frontend_is_skipped_when_index_is_missing(tmp_path):
    app = FastAPI()

    assert mount_frontend(app, Path(tmp_path / "missing-dist")) is False
