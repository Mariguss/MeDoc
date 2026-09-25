import datetime

from pydantic import (
    BaseModel,
)

from app.core.model.inspection import Status
from app.core.schema.base import BaseQuery
from app.util.date import get_now


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

# class InspectionCreate(InspectionBase):
#     ...
#
# class InspectionUpdateByAdmin(InspectionBase):
#     date: datetime.datetime | None = None
#     doctor_id: int | None = None
#     patient_id: int | None = None
#
# class InspectionUpdateByDoctor(InspectionBase):
#     date: datetime.datetime | None = None
#     doctor_id: int | None = None
#     patient_id: int | None = None
#
# class InspectionQuery(BaseQuery):
#     date: datetime.datetime | None = None
#     address: str | None = None
#
#
# class InspectionQueryAdmin(InspectionQuery):
#     doctor_id: int | None = None
#     patient_id: int | None = None


class InspectionCreateAdmin(BaseModel):
    date: datetime.datetime
    address: str
    doctor_id: int
    patient_id: int
    inspection_at: datetime.datetime | None = None
    created_at: datetime.datetime | None = get_now()
    updated_at: datetime.datetime | None = get_now()

# по записи, но осмотра не было
class InspectionUpdateAdmin(BaseModel):
    ...

# добавить для осмотра без записи. в порядке очереди
class InspectionCreateDoctor(BaseModel):
    ...

class InspectionUpdateDoctor(BaseModel):
    address: str | None = None
    symptoms: str | None = None
    instructions: str | None = None
    disease_ids: list[int] | None = None
    prescriptions_create: list[PrescriptionItemCreate] | None = None
    prescriptions_update: list[PrescriptionItemUpdate] | None = None
    prescriptions_delete_ids: list[int] | None = None
    status: Status | None = Status.COMPLETED
    updated_at: datetime.datetime | None = get_now()

class PrescriptionItemCreate(BaseModel):
    medicine_id: int
    intake_method: str | None = None

class PrescriptionItemUpdate(BaseModel):
    id: int
    intake_method: str | None = None
