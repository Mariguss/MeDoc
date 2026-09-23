from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from app.core.dependencies import get_inspection_service
from app.core.schema.base import PaginatedResponse
from app.core.schema.incpection import (
    InspectionResponse,
    InspectionResponseAdmin,
    InspectionUpdateByAdmin,
    InspectionCreate,
)
from app.service.incpection import InspectionService

router = APIRouter(
    prefix="/inspection",
    tags=["inspection"],
)


@router.get(
    "/",
    response_model=PaginatedResponse[InspectionResponse],
    status_code=200,
)
async def get_inspections(
        service: InspectionService = Depends(get_inspection_service),
        page: int = 1,
        page_size: int = 10,
        ordering: str = "-id",
        doctor_id: int | None = None,
        patient_id: int | None = None,
):
    return await service.get_list(
        page=page,
        page_size=page_size,
        ordering=ordering,
        doctor_id=doctor_id,
        patient_id=patient_id,
    )
@router.get(
    "/{id_}",
    response_model=InspectionResponseAdmin,
    status_code=200,
)
async def get_inspection(
        id_: int,
        service: InspectionService = Depends(get_inspection_service),
):
    employee = await service.get_by_id(id_)
    if employee is None:
        raise HTTPException(status_code=404, detail="Запись не найдена")
    return employee

@router.post(
    "/",
    response_model=InspectionResponseAdmin,
    status_code=201,
)
async def create_inspection(
        employee: InspectionCreate,
        service: InspectionService = Depends(get_inspection_service),
) -> InspectionResponseAdmin:
    return await service.add(employee)

@router.patch(
    "/{id_}",
    response_model=InspectionResponseAdmin,
)
async def update_medicine(
        id_: int,
        employee: InspectionUpdateByAdmin,
        service: InspectionService = Depends(get_inspection_service),
):
    return await service.patch(id_, employee)

@router.delete(
    "/{id_}",
    status_code=204,
)
async def delete_medicine(
        id_: int,
        service: InspectionService = Depends(get_inspection_service),
):
    return await service.remove_by_id(id_)
