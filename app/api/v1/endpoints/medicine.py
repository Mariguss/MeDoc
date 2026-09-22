from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import database
from app.core.schema.base import PaginatedResponse
from app.core.schema.medicine import (
    MedicineResponse,
    MedicineResponseAdmin,
    MedicineUpdate,
    MedicineCreate,
)
from app.repository.medicine import MedicineRepository
from app.service.medicine import MedicineService

router = APIRouter(
    prefix="/medicine",
    tags=["medicine"],
)

# app/api/dependencies.py

async def get_medicine_repository(
    session: AsyncSession = Depends(database.get_session),
) -> MedicineRepository:
    return MedicineRepository(session)

async def get_medicine_service(
    repo: MedicineRepository = Depends(get_medicine_repository),
) -> MedicineService:
    return MedicineService(repo)

@router.get(
    "/",
    response_model=PaginatedResponse[MedicineResponse],
    status_code=200,
)
async def get_medicines(
        service: MedicineService = Depends(get_medicine_service),
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
    response_model=MedicineResponseAdmin,
    status_code=200,
)
async def get_medicine(
        id_: int,
        service: MedicineService = Depends(get_medicine_service),
):
    employee = await service.get_by_id(id_)
    if employee is None:
        raise HTTPException(status_code=404, detail="Лекарство не найдено")
    return employee

@router.post(
    "/",
    response_model=MedicineResponseAdmin,
    status_code=201,
)
async def create_medicine(
        employee: MedicineCreate,
        service: MedicineService = Depends(get_medicine_service),
) -> MedicineResponseAdmin:
    return await service.add(employee)

@router.patch(
    "/{id_}",
    response_model=MedicineResponseAdmin,
)
async def update_medicine(
        id_: int,
        employee: MedicineUpdate,
        service: MedicineService = Depends(get_medicine_service),
):
    return await service.patch(id_, employee)

@router.delete(
    "/{id_}",
    status_code=204,
)
async def delete_medicine(
        id_: int,
        service: MedicineService = Depends(get_medicine_service),
):
    return await service.remove_by_id(id_)
