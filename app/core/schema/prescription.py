from pydantic import BaseModel


class PrescriptionCreate(BaseModel):
    medicine_id: int
    intake_method: str | None = None


class PrescriptionUpdate(PrescriptionCreate):
    id: int
