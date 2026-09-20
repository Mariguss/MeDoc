from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from app.core.model import Base
from app.core.model.mixin import IntIdPKMixin

if TYPE_CHECKING:
    ...

class Medicine(Base, IntIdPKMixin):
    name: Mapped[str] = mapped_column(String(50))
    properties: Mapped[str]
