from typing import Annotated

from pydantic import (
    BaseModel,
    Field,
    field_validator,
)

from app.util.hashing import get_password_hash


class EmployeeAuth(BaseModel):
    login: Annotated[str | None, Field(min_length=5, max_length=15)]
    password: Annotated[str, Field(min_length=8, max_length=128)]

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
