from sqlalchemy import ForeignKey
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from app.core.model import Base
from app.core.model.mixin import IntIdPKMixin


class InspectionDisease(Base, IntIdPKMixin):
    inspection_id: Mapped[int] = mapped_column(
        ForeignKey("inspections.id", ondelete="CASCADE"),
    )
    disease_id: Mapped[int] = mapped_column(
        ForeignKey("diseases.id", ondelete="CASCADE"),
    )
