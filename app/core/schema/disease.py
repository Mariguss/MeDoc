from typing import Annotated

from pydantic import (
    BaseModel,
    Field,
)

from app.core.schema.base import BaseQuery


class DiseaseBase(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=50)]

class DiseaseResponse(DiseaseBase):

    model_config = {"from_attributes": True}

class DiseaseResponseAdmin(DiseaseResponse):
    id: int

class DiseaseCreate(DiseaseBase):
    ...

class DiseaseUpdate(DiseaseBase):
    name: Annotated[str | None, Field(min_length=1, max_length=50)] = None

class DiseaseQuery(BaseQuery, DiseaseBase):
    ...