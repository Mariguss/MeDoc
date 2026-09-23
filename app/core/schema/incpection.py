import datetime

from pydantic import (
    BaseModel,
)

from app.core.schema.base import BaseQuery


class InspectionBase(BaseModel):
    date: datetime.datetime
    address: str | None = None
    symptoms: str | None = None
    instructions: str | None = None
    doctor_id: int
    patient_id: int


class InspectionResponse(InspectionBase):

    model_config = {"from_attributes": True}

class InspectionResponseAdmin(InspectionResponse):
    id: int

class InspectionCreate(InspectionBase):
    ...

class InspectionUpdateByAdmin(InspectionBase):
    date: datetime.datetime | None = None
    doctor_id: int | None = None
    patient_id: int | None = None

class InspectionUpdateByDoctor(InspectionBase):
    date: datetime.datetime | None = None
    doctor_id: int | None = None
    patient_id: int | None = None

class InspectionQuery(BaseQuery):
    date: datetime.datetime | None = None
    address: str | None = None


class InspectionQueryAdmin(InspectionQuery):
    doctor_id: int | None = None
    patient_id: int | None = None
