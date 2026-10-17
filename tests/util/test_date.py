from datetime import UTC, datetime

from app.util.date import get_now


def test_get_now(monkeypatch):
    fixed_time = datetime(2026, 10, 11, 22, 0, 0, tzinfo=UTC)

    class MockDatetime:
        @classmethod
        def now(cls, tz=None):
            return fixed_time

    monkeypatch.setattr("app.util.date.datetime", MockDatetime)

    assert get_now() == fixed_time
