import datetime
import enum
from typing import TYPE_CHECKING

from sqlalchemy import (
    String,
    Enum,
    Date,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from app.core.model.base import Base
from app.core.model.mixin import IntIdPKMixin
from app.core.model.mixin.created_at import CreatedAtMixin
from app.core.model.mixin.updated_at import UpdatedAtMixin

if TYPE_CHECKING:
    ...

class Sex(str, enum.Enum):
    MALE = "m"
    FEMALE = "f"

# в будущем добавить паспортные данные или номер телефона
class Patient(Base, IntIdPKMixin, CreatedAtMixin, UpdatedAtMixin):
    name: Mapped[str] = mapped_column(String(50))
    sex: Mapped[Sex] = mapped_column(
        Enum(Sex),
        default=Sex.FEMALE,
    )
    born_date: Mapped[datetime.date] = mapped_column(
        Date,
    )
    home_address: Mapped[str | None] = mapped_column(String(100))
    phone_number: Mapped[str | None] = mapped_column(String(11))
