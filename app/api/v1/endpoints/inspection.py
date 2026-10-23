from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
)

from app.core.dependencies import (
    auth_bearer,
    get_current_user_id,
    get_inspection_service,
    required_roles,
)
from app.core.schema.base import PaginatedResponse
from app.core.schema.inspection import (
    InspectionCreateAdmin,
    InspectionCreateDoctor,
    InspectionCreateDoctorInternal,
    InspectionPerDateRequest,
    InspectionQueryAdmin,
    InspectionQueryDoctor,
    InspectionQueryResponseAdmin,
    InspectionQueryResponseDoctor,
    InspectionResponse,
    InspectionResponseAdmin,
    InspectionResponseDoctor,
    InspectionUpdateAdmin,
    InspectionUpdateDoctor,
)
from app.service.inspection import InspectionService

router = APIRouter(
    prefix="/inspection",
    tags=["inspection"],
    dependencies=[Depends(auth_bearer)],
)


@router.patch(
    "/doctor/",
    response_model=PaginatedResponse[InspectionQueryResponseDoctor],
)
async def get_inspections_by_doctor(
    service: Annotated[InspectionService, Depends(get_inspection_service)],
    inspection_query: InspectionQueryDoctor,
    _role: str = Depends(required_roles(["doctor"])),
):
    return await service.get_list(**inspection_query.model_dump(exclude_unset=True))


@router.patch(
    "/admin/",
    response_model=PaginatedResponse[InspectionQueryResponseAdmin],
)
async def get_inspections_by_admin(
    service: Annotated[InspectionService, Depends(get_inspection_service)],
    inspection_query: InspectionQueryAdmin,
    _role: str = Depends(required_roles(["admin"])),
):
    return await service.get_list(**inspection_query.model_dump(exclude_unset=True))


@router.get(
    "/doctor/{id_}",
    response_model=InspectionResponse,
    status_code=200,
)
async def get_inspection_by_doctor(
    id_: int,
    service: Annotated[InspectionService, Depends(get_inspection_service)],
    _role: str = Depends(required_roles(["doctor"])),
) -> InspectionResponse:
    return await service.get_by_id(id_)


@router.get(
    "/admin/{id_}",
    response_model=InspectionResponseAdmin,
    status_code=200,
)
async def get_inspection_by_admin(
    id_: int,
    service: Annotated[InspectionService, Depends(get_inspection_service)],
    _role: str = Depends(required_roles(["admin"])),
) -> InspectionResponseAdmin:
    return await service.get_by_id(id_)


@router.post(
    "/admin/",
    response_model=InspectionResponseAdmin,
    status_code=201,
)
async def create_inspection_by_admin(
    inspection: InspectionCreateAdmin,
    service: Annotated[InspectionService, Depends(get_inspection_service)],
    _role: str = Depends(required_roles(["admin"])),
) -> InspectionResponseAdmin:
    return await service.add_by_admin(inspection)


@router.post(
    "/doctor/",
    response_model=InspectionResponseDoctor,
    status_code=201,
)
async def create_inspection_by_doctor(
    inspection: InspectionCreateDoctor,
    service: Annotated[InspectionService, Depends(get_inspection_service)],
    doctor_id: int = Depends(get_current_user_id),
    _role: str = Depends(required_roles(["doctor"])),
) -> InspectionResponseDoctor:
    print("doctor_id in api", doctor_id)
    data = InspectionCreateDoctorInternal(
        **inspection.model_dump(), doctor_id=doctor_id
    )
    return await service.add_by_doctor(data)


@router.patch(
    "/admin/{id_}",
    response_model=InspectionResponseAdmin,
)
async def update_inspection_by_admin(
    id_: int,
    inspection: InspectionUpdateAdmin,
    service: Annotated[InspectionService, Depends(get_inspection_service)],
    _role: str = Depends(required_roles(["admin"])),
) -> InspectionResponseAdmin:
    return await service.patch_by_admin(id_, inspection)


@router.patch(
    "/doctor/{id_}",
    response_model=InspectionResponseDoctor,
)
async def update_inspection_by_doctor(
    id_: int,
    inspection: InspectionUpdateDoctor,
    service: Annotated[InspectionService, Depends(get_inspection_service)],
    _role: str = Depends(required_roles(["doctor"])),
) -> InspectionResponseDoctor:
    return await service.patch_by_doctor(id_, inspection)


@router.get("/statistics/disease_per_patient/{id_}")
async def get_inspection_statistics_disease_per_patient(
    id_: int,
    service: Annotated[InspectionService, Depends(get_inspection_service)],
) -> int:
    return await service.disease_per_patient(id_)


@router.post("/statistics/inspection_per_date/")
async def get_inspection_statistics_inspection_per_date(
    schema: InspectionPerDateRequest,
    service: Annotated[InspectionService, Depends(get_inspection_service)],
) -> list:
    return await service.inspection_per_day(schema)
