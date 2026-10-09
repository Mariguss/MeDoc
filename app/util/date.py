from datetime import (
    UTC,
    datetime,
)


def get_now():
    return datetime.now(UTC)
