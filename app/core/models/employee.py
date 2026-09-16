import enum
from typing import TYPE_CHECKING

from sqlalchemy import (
    String,
    Enum,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from app.core.models import Base
from app.core.models.mixins import IntIdPKMixin

if TYPE_CHECKING:
    ...

class Role(enum.Enum):
    DOCTOR = 1
    ADMIN = 2

class Employee(Base, IntIdPKMixin):
    login: Mapped[str] = mapped_column(String(15))
    password_hash: Mapped[str]
    name: Mapped[str] = mapped_column(String(50))
    role: Mapped[Role] = mapped_column(
        Enum(Role),
        default=Role.DOCTOR,
    )
