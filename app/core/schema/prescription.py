from pydantic import BaseModel

from app.core.schema.medicine import MedicineResponse


class PrescriptionCreate(BaseModel):
    medicine_id: int
    intake_method: str | None = None


class PrescriptionUpdate(PrescriptionCreate):
    id: int


class PrescriptionResponse(BaseModel):
    medicine_id: int
    intake_method: str | None
    medicine: MedicineResponse
    model_config = {"from_attributes": True}
