import datetime
from typing import Annotated

from pydantic import (
    BaseModel,
    Field,
)

from app.core.model.patient import Sex
from app.core.schema.base import BaseQuery


class PatientBase(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=50)]
    sex: Sex | None = Sex.FEMALE
    born_date: datetime.date
    home_address: str | None = None

class PatientResponse(PatientBase):

    model_config = {"from_attributes": True}

class PatientResponseAdmin(PatientResponse):
    id: int

class PatientCreate(PatientBase):
    ...

class PatientUpdate(PatientBase):
    name: Annotated[str | None, Field(min_length=1, max_length=50)] = None
    sex: Sex | None = Sex.FEMALE
    born_date: datetime.date | None = None
    home_address: str | None = None

class PatientQuery(BaseQuery, PatientBase):
    ...