import datetime

from sqlalchemy import DateTime
from sqlalchemy.orm import (
    Mapped,
    mapped_column
)

from app.util.date import get_now


class CreatedAtMixin:
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=get_now())
