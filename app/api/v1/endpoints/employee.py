from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import database
from app.core.schema.base import PaginatedResponse
from app.core.schema.employee import (
    EmployeeResponseAdmin,
    EmployeeCreate,
    EmployeeUpdate,
    EmployeeResponse,
)
from app.repository.employee import EmployeeRepository
from app.service.employee import EmployeeService

router = APIRouter(
    prefix="/employee",
    tags=["employee"],
)

# app/api/dependencies.py

async def get_employee_repository(
    session: AsyncSession = Depends(database.get_session),
) -> EmployeeRepository:
    return EmployeeRepository(session)

async def get_employee_service(
    repo: EmployeeRepository = Depends(get_employee_repository),
) -> EmployeeService:
    return EmployeeService(repo)

@router.get(
    "/",
    response_model=PaginatedResponse[EmployeeResponse],
    status_code=200,
)
async def get_employees(
        service: EmployeeService = Depends(get_employee_service),
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
    response_model=EmployeeResponseAdmin,
    status_code=200,
)
async def get_employee(
        id_: int,
        service: EmployeeService = Depends(get_employee_service),
):
    employee = await service.get_by_id(id_)
    if employee is None:
        raise HTTPException(status_code=404, detail="Сотрудник не найден")
    return employee

@router.post(
    "/",
    response_model=EmployeeResponseAdmin,
    status_code=201,
)
async def create_employee(
        employee: EmployeeCreate,
        service: EmployeeService = Depends(get_employee_service),
) -> EmployeeResponseAdmin:
    return await service.add(employee)

@router.patch(
    "/{id_}",
    response_model=EmployeeResponseAdmin,
)
async def update_employee(
        id_: int,
        employee: EmployeeUpdate,
        service: EmployeeService = Depends(get_employee_service),
):
    return await service.patch(id_, employee)

@router.delete(
    "/{id_}",
    status_code=204,
)
async def delete_employee(
        id_: int,
        service: EmployeeService = Depends(get_employee_service),
):
    return await service.remove_by_id(id_)
