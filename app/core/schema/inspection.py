import datetime

from pydantic import (
    BaseModel,
)

from app.core.model.inspection import Status
from app.core.schema.prescription import (
    PrescriptionCreate,
    PrescriptionUpdate,
)


class InspectionBase(BaseModel):
    address: str | None = None
    symptoms: str | None = None
    instructions: str | None = None
    doctor_id: int
    patient_id: int
    inspection_at: datetime.datetime | None = None


class InspectionResponse(BaseModel):
    inspection_at: datetime.datetime | None = None
    created_at: datetime.datetime
    updated_at: datetime.datetime
    address: str | None = None
    doctor_id: int
    patient_id: int
    model_config = {"from_attributes": True}


class InspectionResponseAdmin(InspectionResponse):
    id: int


class InspectionResponseDoctor(InspectionResponseAdmin):
    symptoms: str | None = None
    instructions: str | None = None


# class InspectionQuery(BaseQuery):
#     date: datetime.datetime | None = None
#     address: str | None = None
#
#
# class InspectionQueryAdmin(InspectionQuery):
#     doctor_id: int | None = None
#     patient_id: int | None = None


class InspectionCreateAdmin(BaseModel):
    address: str | None = "ул. Малая Семеновская д.13"
    doctor_id: int
    patient_id: int
    inspection_at: datetime.datetime | None = None


# по записи, но осмотра не было
class InspectionUpdateAdmin(BaseModel):
    doctor_id: int | None = None
    patient_id: int | None = None
    address: str | None = None
    inspection_at: datetime.datetime | None = None


# добавить для осмотра без записи. в порядке очереди
class InspectionCreateDoctor(BaseModel):
    patient_id: int
    address: str | None = "ул. Малая Семеновская д.13"
    symptoms: str | None = None
    instructions: str | None = None
    disease_ids: list[int] | None = None
    prescriptions_create: list[PrescriptionCreate] | None = None
    status: Status | None = Status.COMPLETED
    inspection_at: datetime.datetime | None = None


class InspectionCreateDoctorInternal(InspectionCreateDoctor):
    doctor_id: int


class InspectionUpdateDoctor(BaseModel):
    patient_id: int | None = None
    address: str | None = None
    symptoms: str | None = None
    instructions: str | None = None
    status: Status | None = None
    disease_ids: list[int] | None = None
    prescriptions_update: list[PrescriptionUpdate] | None = None
    prescriptions_delete_ids: list[int] | None = None
    prescriptions_create: list[PrescriptionCreate] | None = None
    inspection_at: datetime.datetime | None = None


class InspectionPerDateRequest(BaseModel):
    status: Status | None = Status.COMPLETED
    start_date: datetime.datetime | None = None
    end_date: datetime.datetime | None = None
