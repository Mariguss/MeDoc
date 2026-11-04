from datetime import (
    UTC,
    datetime,
)


def get_now():
    return datetime.now(UTC)


def get_now_naive():
    """Текущее UTC-время без часового пояса (для колонок TIMESTAMP WITHOUT TIME ZONE)."""
    return datetime.now(UTC).replace(tzinfo=None)
