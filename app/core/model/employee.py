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

from app.core.model.base import Base
from app.core.model.mixin import IntIdPKMixin

if TYPE_CHECKING:
    ...

class Role(str, enum.Enum):
    DOCTOR = "doctor"
    ADMIN = "admin"

class Employee(Base, IntIdPKMixin):
    login: Mapped[str] = mapped_column(String(15), unique=True)
    password_hash:  Mapped[str] = mapped_column(String(255))
    name: Mapped[str] = mapped_column(String(50))
    role: Mapped[Role] = mapped_column(
        Enum(Role),
        default=Role.DOCTOR,
    )
    speciality: Mapped[str | None] = mapped_column(String(50))
