import json


def test_scheduler_once_cli_outputs_json(monkeypatch, capsys):
    from app.cli.scheduler_once import main

    def fake_run_due_scheduler(db, user_id: int):
        assert user_id == 7
        return {"ran": False, "reason": "scheduler disabled", "result": None}

    monkeypatch.setattr("app.cli.scheduler_once.run_due_scheduler", fake_run_due_scheduler)

    exit_code = main(["--user-id", "7"])

    assert exit_code == 0
    output = json.loads(capsys.readouterr().out)
    assert output == {"ran": False, "reason": "scheduler disabled", "result": None}
