from domain import logger


def test_log_event_and_read_recent_logs(tmp_path, monkeypatch):
    logs_dir = tmp_path / "logs_test"
    log_file = logs_dir / "app_events.jsonl"

    monkeypatch.setattr(logger, "LOGS_DIR", logs_dir)
    monkeypatch.setattr(logger, "LOG_FILE", log_file)

    logger.log_event("test_event", {"country": "México"})
    logger.log_event("other_event", {"ok": True})

    events = logger.read_recent_logs(limit=10)

    assert len(events) == 2
    assert events[0]["event_type"] == "other_event"
    assert events[1]["event_type"] == "test_event"


def test_get_log_stats(tmp_path, monkeypatch):
    logs_dir = tmp_path / "logs_test"
    log_file = logs_dir / "app_events.jsonl"

    monkeypatch.setattr(logger, "LOGS_DIR", logs_dir)
    monkeypatch.setattr(logger, "LOG_FILE", log_file)

    logger.log_event("event_a", {})
    logger.log_event("event_b", {})

    stats = logger.get_log_stats()

    assert stats["total_events"] == 2
    assert stats["log_file"].endswith("app_events.jsonl")


def test_clear_logs(tmp_path, monkeypatch):
    logs_dir = tmp_path / "logs_test"
    log_file = logs_dir / "app_events.jsonl"

    monkeypatch.setattr(logger, "LOGS_DIR", logs_dir)
    monkeypatch.setattr(logger, "LOG_FILE", log_file)

    logger.log_event("event_a", {})
    logger.log_event("event_b", {})

    deleted = logger.clear_logs()

    assert deleted == 2
    assert logger.read_recent_logs(limit=10) == []