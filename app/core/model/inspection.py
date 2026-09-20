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
)

from app.core.model import Base
from app.core.model.mixin import IntIdPKMixin

if TYPE_CHECKING:
    ...

class Inspection(Base, IntIdPKMixin):
    date: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    address: Mapped[str]
    symptoms: Mapped[str]
    instructions: Mapped[str]

    # будут изменения?
    doctor_id: Mapped[int] = mapped_column(
        ForeignKey('doctors.id'),
        on_delete='RESTRICT',
    )
    patient_id: Mapped[int] = mapped_column(
        ForeignKey('patients.id'),
        on_delete='RESTRICT',
    )
    disease_id: Mapped[int | None] = mapped_column(
        ForeignKey('disease.id'),
        ondelete='SET NULL',
    )
