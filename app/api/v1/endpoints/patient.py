from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import database
from app.core.schema.base import PaginatedResponse
from app.core.schema.patient import (
    PatientResponse,
    PatientResponseAdmin,
    PatientCreate,
    PatientUpdate,
)
from app.repository.patient import PatientRepository
from app.service.patient import PatientService

router = APIRouter(
    prefix="/patient",
    tags=["patient"],
)

# app/api/dependencies.py

async def get_patient_repository(
    session: AsyncSession = Depends(database.get_session),
) -> PatientRepository:
    return PatientRepository(session)

async def get_patient_service(
    repo: PatientRepository = Depends(get_patient_repository),
) -> PatientService:
    return PatientService(repo)

@router.get(
    "/",
    response_model=PaginatedResponse[PatientResponse],
    status_code=200,
)
async def get_patients(
        service: PatientService = Depends(get_patient_service),
        page: int = 1,
        page_size: int = 10,
        ordering: str = "-id",
):
    return await service.get_list(
        page=page,
        page_size=page_size,
        ordering=ordering,
    )
@router.get(
    "/{id_}",
    response_model=PatientResponseAdmin,
    status_code=200,
)
async def get_patient(
        id_: int,
        service: PatientService = Depends(get_patient_service),
):
    employee = await service.get_by_id(id_)
    if employee is None:
        raise HTTPException(status_code=404, detail="Пациент не найден")
    return employee

@router.post(
    "/",
    response_model=PatientResponseAdmin,
    status_code=201,
)
async def create_patient(
        employee: PatientCreate,
        service: PatientService = Depends(get_patient_service),
) -> PatientResponseAdmin:
    return await service.add(employee)

@router.patch(
    "/{id_}",
    response_model=PatientResponseAdmin,
)
async def update_patient(
        id_: int,
        employee: PatientUpdate,
        service: PatientService = Depends(get_patient_service),
):
    return await service.patch(id_, employee)

@router.delete(
    "/{id_}",
    status_code=204,
)
async def delete_patient(
        id_: int,
        service: PatientService = Depends(get_patient_service),
):
    return await service.remove_by_id(id_)
