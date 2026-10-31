from typing import (
    Annotated,
)

from pydantic import (
    BaseModel,
    Field,
)


class BaseQuery(BaseModel):
    page: Annotated[int, Field(ge=1)] = 1
    page_size: Annotated[int, Field(ge=1)] = 10
    ordering: str = "-id"


class PaginatedResponse[T](BaseModel):
    founds: list[T]
    total_count: int
