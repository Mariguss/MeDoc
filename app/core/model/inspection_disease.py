from sqlalchemy import (
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from app.core.model import Base
from app.core.model.mixin import IntIdPKMixin


class InspectionDisease(Base, IntIdPKMixin):
    __table_args__ = (
        UniqueConstraint("inspection_id", "disease_id"),
    )
    inspection_id: Mapped[int] = mapped_column(
        ForeignKey("inspections.id", ondelete="CASCADE"),
    )
    disease_id: Mapped[int] = mapped_column(
        ForeignKey("diseases.id", ondelete="CASCADE"),
    )
