from fastapi import (
    APIRouter,
    Depends,
)

from app.core.dependencies import get_inspection_service, required_roles, auth_bearer, get_current_user
from app.core.model.employee import Role
from app.core.schema.inspection import (
    InspectionResponseAdmin,
    InspectionCreateAdmin,
    InspectionUpdateDoctor, InspectionPerDateRequest, InspectionCreateDoctor, InspectionResponseDoctor,
    InspectionUpdateAdmin,
)
from app.service.inspection import InspectionService

router = APIRouter(
    prefix="/inspection",
    tags=["inspection"],
    dependencies=[Depends(auth_bearer)],
)

#
# @router.get(
#     "/",
#     response_model=PaginatedResponse[InspectionResponse],
#     status_code=200,
# )
# async def get_inspections(
#         service: InspectionService = Depends(get_inspection_service),
#         page: int = 1,
#         page_size: int = 10,
#         ordering: str = "-id",
#         doctor_id: int | None = None,
#         patient_id: int | None = None,
# ):
#     return await service.get_list(
#         page=page,
#         page_size=page_size,
#         ordering=ordering,
#         doctor_id=doctor_id,
#         patient_id=patient_id,
#     )
# @router.get(
#     "/{id_}",
#     response_model=InspectionResponseAdmin,
#     status_code=200,
# )
# async def get_inspection(
#         id_: int,
#         service: InspectionService = Depends(get_inspection_service),
# ):
#     employee = await service.get_by_id(id_)
#     if employee is None:
#         raise HTTPException(status_code=404, detail="Запись не найдена")
#     return employee

@router.post(
    "/admin/",
    response_model=InspectionResponseAdmin,
    status_code=201,
)
async def create_inspection_by_admin(
        inspection: InspectionCreateAdmin,
        service: InspectionService = Depends(get_inspection_service),
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
        service: InspectionService = Depends(get_inspection_service),
        _role: str = Depends(required_roles(["doctor"])),
) -> InspectionResponseDoctor:
    doctor_id_ = get_current_user().get("id")
    return await service.add_by_doctor(doctor_id_, inspection)

@router.patch(
    "/{id_}",
    response_model=InspectionResponseAdmin,
)
async def update_inspection_by_admin(
        id_: int,
        inspection: InspectionUpdateAdmin,
        service: InspectionService = Depends(get_inspection_service),
        _role: str = Depends(required_roles(["admin"])),
):
    return await service.patch_by_admin(id_, inspection)

@router.patch(
    "/{id_}",
    response_model=InspectionResponseDoctor,
)
async def update_inspection_by_doctor(
        id_: int,
        inspection: InspectionUpdateDoctor,
        service: InspectionService = Depends(get_inspection_service),
        _role: str = Depends(required_roles(["doctor"])),
):
    return await service.patch_by_doctor(id_, inspection)

#
# @router.delete(
#     "/{id_}",
#     status_code=204,
# )
# async def delete_medicine(
#         id_: int,
#         service: InspectionService = Depends(get_inspection_service),
# ):
#     return await service.remove_by_id(id_)

@router.get("/statistics/disease_per_patient/{id_}")
async def get_inspection_statistics_disease_per_patient(
        id_: int,
        service: InspectionService = Depends(get_inspection_service),
) -> int:
    return await service.disease_per_patient(id_)

@router.put("/statistics/inspection_per_date/")
async def get_inspection_statistics_inspection_per_date(
        schema: InspectionPerDateRequest,
        service: InspectionService = Depends(get_inspection_service),
) -> list:
    return await service.inspection_per_day(schema)
