from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.core.model.base import Base
from app.core.model.mixin import IntIdPKMixin

if TYPE_CHECKING:
    from app.core.model.inspection import Inspection

class Disease(Base, IntIdPKMixin):
    name: Mapped[str] = mapped_column(String(50), unique=True)

    inspections: Mapped[list["Inspection"]] = relationship(
        "Inspection",
        secondary="inspectiondiseases",
        back_populates="diseases",
    )
