from typing import Annotated

from pydantic import (
    BaseModel,
    Field,
)

from app.core.schema.base import BaseQuery


class MedicineBase(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=50)]
    properties: str
    side_effects: str

class MedicineResponse(MedicineBase):

    model_config = {"from_attributes": True}

class MedicineResponseAdmin(MedicineResponse):
    id: int

class MedicineCreate(MedicineBase):
    ...

class MedicineUpdate(MedicineBase):
    name: Annotated[str | None, Field(min_length=1, max_length=50)] = None
    properties: str | None = 0
    side_effects: str | None = 0

class MedicineQuery(BaseQuery, MedicineBase):
    ...