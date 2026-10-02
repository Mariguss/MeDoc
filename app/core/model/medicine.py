from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from app.core.model.base import BaseWithId

if TYPE_CHECKING:
    ...

class Medicine(BaseWithId):
    name: Mapped[str] = mapped_column(String(50), unique=True)
    properties: Mapped[str]
    side_effects: Mapped[str]
