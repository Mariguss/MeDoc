from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
)

from app.core.dependencies import get_employee_service, required_roles
from app.core.schema.base import PaginatedResponse
from app.core.schema.employee import (
    EmployeeCreate,
    EmployeeResponse,
    EmployeeResponseAdmin,
    EmployeeUpdate,
)
from app.service.employee import EmployeeService

router = APIRouter(
    prefix="/employee",
    tags=["employee", "administration"],
    dependencies=[Depends(required_roles(["admin"]))],
)


@router.get(
    "/",
    response_model=PaginatedResponse[EmployeeResponse],
    status_code=200,
)
async def get_employees(
    service: Annotated[EmployeeService, Depends(get_employee_service)],
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
    service: Annotated[EmployeeService, Depends(get_employee_service)],
):
    return await service.get_by_id(id_)


@router.post(
    "/",
    response_model=EmployeeResponseAdmin,
    status_code=201,
)
async def create_employee(
    employee: EmployeeCreate,
    service: Annotated[EmployeeService, Depends(get_employee_service)],
) -> EmployeeResponseAdmin:
    return await service.add(employee)


@router.patch(
    "/{id_}",
    response_model=EmployeeResponseAdmin,
)
async def update_employee(
    id_: int,
    employee: EmployeeUpdate,
    service: Annotated[EmployeeService, Depends(get_employee_service)],
):
    return await service.patch(id_, employee)


@router.delete(
    "/{id_}",
    status_code=204,
)
async def delete_employee(
    id_: int,
    service: Annotated[EmployeeService, Depends(get_employee_service)],
):
    return await service.remove_by_id(id_)
