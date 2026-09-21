from typing import Annotated

from pydantic import (
    BaseModel,
    Field,
)


class BaseQuery(BaseModel):
    page: Annotated[int, Field(ge=1)] = 1
    page_size: Annotated[int, Field(ge=1, le=100)] = 10
    sort_by: str | None = None
    sort_order: Annotated[str | None, Field(pattern="^(asc|desc)$")] = "asc"
