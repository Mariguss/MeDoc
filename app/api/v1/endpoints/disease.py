from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from app.core.dependencies import get_disease_service, auth_bearer
from app.core.schema.base import PaginatedResponse
from app.core.schema.disease import (
    DiseaseResponse,
    DiseaseResponseAdmin,
    DiseaseCreate,
    DiseaseUpdate,
)
from app.service.disease import DiseaseService

router = APIRouter(
    prefix="/disease",
    tags=["disease", "administration"],
    dependencies=[Depends(auth_bearer)],
)


@router.get(
    "/",
    response_model=PaginatedResponse[DiseaseResponse],
    status_code=200,
)
async def get_diseases(
    service: DiseaseService = Depends(get_disease_service),
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
    response_model=DiseaseResponseAdmin,
    status_code=200,
)
async def get_disease(
    id_: int,
    service: DiseaseService = Depends(get_disease_service),
):
    disease = await service.get_by_id(id_)
    if disease is None:
        raise HTTPException(status_code=404, detail="Болезнь не найдена")
    return disease


@router.post(
    "/",
    response_model=DiseaseResponseAdmin,
    status_code=201,
)
async def create_disease(
    disease: DiseaseCreate,
    service: DiseaseService = Depends(get_disease_service),
) -> DiseaseResponseAdmin:
    return await service.add(disease)


@router.patch(
    "/{id_}",
    response_model=DiseaseResponseAdmin,
)
async def update_disease(
    id_: int,
    disease: DiseaseUpdate,
    service: DiseaseService = Depends(get_disease_service),
):
    return await service.patch(id_, disease)


@router.delete(
    "/{id_}",
    status_code=204,
)
async def delete_disease(
    id_: int,
    service: DiseaseService = Depends(get_disease_service),
):
    return await service.remove_by_id(id_)
