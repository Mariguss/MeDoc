from typing import TYPE_CHECKING

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

if TYPE_CHECKING:
    ...

class Prescriptions(Base, IntIdPKMixin):
    __table_args__ = (
        UniqueConstraint(
            'inspection_id',
            'medicine_id',
            'intake_method',
            name='idx_unique_inspection_medicine_intake'
        )
    )
    inspection_id: Mapped[int] = mapped_column(
        ForeignKey("inspections.id", ondelete="CASCADE"),
    )
    medicine_id: Mapped[int] = mapped_column(
        ForeignKey("medicines.id", ondelete="RESTRICT"),
    )

    intake_method: Mapped[str]
    side_effects: Mapped[str | None]
