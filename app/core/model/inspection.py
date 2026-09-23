import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    DateTime,
    func,
    ForeignKey,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.core.model.base import Base
from app.core.model.mixin import IntIdPKMixin

if TYPE_CHECKING:
    from app.core.model.disease import Disease

class Inspection(Base, IntIdPKMixin):
    date: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    address: Mapped[str | None] = mapped_column(default="адрес больницы")
    symptoms: Mapped[str | None]
    instructions: Mapped[str | None]

    doctor_id: Mapped[int] = mapped_column(
        ForeignKey('employees.id', ondelete='RESTRICT'),
    )
    patient_id: Mapped[int] = mapped_column(
        ForeignKey('patients.id', ondelete='RESTRICT'),
    )

    diseases: Mapped[list["Disease"]] = relationship(
        "Disease",
        secondary="inspectiondiseases",
        back_populates="inspections",
    )
