import datetime
import enum
from typing import TYPE_CHECKING

from sqlalchemy import (
    String,
    Enum,
    DateTime,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from app.core.model import Base
from app.core.model.mixin import IntIdPKMixin

if TYPE_CHECKING:
    ...

class Sex(enum.Enum):
    MALE = 1
    FEMALE = 2

class Patient(Base, IntIdPKMixin):
    name: Mapped[str] = mapped_column(String(50))
    sex: Mapped[Sex] = mapped_column(
        Enum(Sex),
        default=Sex.FEMALE,
    )
    born_date: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
    )
    home_address: Mapped[str]
