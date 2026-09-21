import re
from typing import Annotated

from pydantic import (
    BaseModel,
    Field,
    field_validator,
)

from app.core.model.employee import Role
from app.core.schema.base import BaseQuery
from app.util.hashing import get_password_hash


class EmployeeBase(BaseModel):
    login: Annotated[str, Field(min_length=5, max_length=15)]
    name: Annotated[str, Field(min_length=1, max_length=50)]
    role: Role | None = Role.DOCTOR
    speciality: Annotated[str | None, Field(min_length=1, max_length=50)] = None

    @field_validator("login")
    @classmethod
    def _validate_login(cls, v: str) -> str:
        if not re.fullmatch(r"[a-zA-Z0-9_]+", v):
            raise ValueError("Логин может содержать только латиницу, цифры и _")
        return v

class EmployeeResponse(BaseModel):
    login: str
    name: str
    speciality: str | None

    model_config = {"from_attributes": True}

class EmployeeResponseAdmin(EmployeeResponse):
    id: int
    role: Role

class EmployeeCreate(EmployeeBase):
    password_hash: Annotated[str, Field(alias="password", min_length=8, max_length=128)]

    @field_validator("password_hash")
    @classmethod
    def _validate_password(cls, v: str) -> str:
        if not re.search(r"[A-Z]", v):
            raise ValueError("Пароль должен содержать заглавную букву")
        if not re.search(r"[a-z]", v):
            raise ValueError("Пароль должен содержать строчную букву")
        if not re.search(r"\d", v):
            raise ValueError("Пароль должен содержать цифру")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            raise ValueError("Пароль должен содержать спецсимвол")
        return get_password_hash(v)

class EmployeeUpdate(EmployeeBase):
    login: Annotated[str | None, Field(min_length=5, max_length=15)] = None
    name: Annotated[str | None, Field(min_length=1, max_length=50)] = None
    role: Role | None = None
    speciality: Annotated[str | None, Field(min_length=1, max_length=50)] = None

class EmployeeQuery(BaseQuery):
    login: str | None = None
    name: str | None = None
    speciality: str | None = None

class EmployeeQueryAdmin(EmployeeQuery):
    role: Role | None = None
