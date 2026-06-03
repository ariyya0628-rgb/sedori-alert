import json

from app.services.adapters.base import ScrapedProduct


def test_check_shops_once_cli_outputs_per_shop_results(monkeypatch, capsys):
    from app.cli.check_shops_once import main

    def fake_success(keyword: str, limit: int):
        assert keyword == "レコルト"
        assert limit == 2
        return [
            ScrapedProduct(
                shop_code="offmall",
                external_product_id="ok-1",
                title="レコルト ホットプレート",
                price=3980,
                product_url="https://example.com/ok-1",
            )
        ]

    def fake_failure(keyword: str, limit: int):
        raise RuntimeError("HTTP 403 Forbidden")

    monkeypatch.setattr(
        "app.cli.check_shops_once.SHOP_FETCHERS",
        {"offmall": fake_success, "secondstreet": fake_failure},
    )

    exit_code = main(["--keyword", "レコルト", "--limit", "2"])

    assert exit_code == 0
    output = json.loads(capsys.readouterr().out)
    assert output["keyword"] == "レコルト"
    assert output["results"][0]["shop_code"] == "offmall"
    assert output["results"][0]["status"] == "success"
    assert output["results"][0]["count"] == 1
    assert output["results"][1]["shop_code"] == "secondstreet"
    assert output["results"][1]["status"] == "failed"
    assert output["results"][1]["error"] == "HTTP 403 Forbidden"
