import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    DateTime,
    func,
    ForeignKey, Enum,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.core.model.base import Base
from app.core.model.mixin import IntIdPKMixin
from app.core.model.mixin.created_at import CreatedAtMixin
from app.core.model.mixin.updated_at import UpdatedAtMixin

if TYPE_CHECKING:
    from app.core.model.disease import Disease

class Status(str, Enum):
    SCHEDULED = "scheduled"        # Запланирован — приём создан, ждём пациента
    COMPLETED = "completed"        # Завершён — осмотр окончен, заключение внесено
    CANCELLED = "cancelled"        # Отменён — приём отменён (пациент или врач)
    NO_SHOW = "no_show"            # Неявка — пациент не пришёл на запланированный приём


class Inspection(Base, IntIdPKMixin, CreatedAtMixin, UpdatedAtMixin):
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

    status: Mapped[Status | None] = mapped_column(default=Status.SCHEDULED)

    inspection_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(timezone=True),
    )

    diseases: Mapped[list["Disease"]] = relationship(
        "Disease",
        secondary="inspectiondiseases",
        back_populates="inspections",
    )
