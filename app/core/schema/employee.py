import re
from typing import Annotated

from pydantic import (
    BaseModel,
    Field,
    field_validator,
)

from app.core.model.employee import Role
from app.util.hashing import get_password_hash


class EmployeeRead(BaseModel):
    id: int
    login: str
    name: str
    role: Role

    model_config = {"from_attributes": True}


class EmployeeCreate(BaseModel):
    login: Annotated[str, Field(min_length=5, max_length=15)]
    password_hash: Annotated[str, Field(alias="password", min_length=8, max_length=128)]
    name: Annotated[str, Field(min_length=1, max_length=50)]
    role: Role | None = Role.DOCTOR

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

    @field_validator("login")
    @classmethod
    def _validate_login(cls, v: str) -> str:
        if not re.fullmatch(r"[a-zA-Z0-9_]+", v):
            raise ValueError("Логин может содержать только латиницу, цифры и _")
        return v
