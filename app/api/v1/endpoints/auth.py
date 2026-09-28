from fastapi import (
    APIRouter,
    Depends,
    Response,
    Cookie,
)

from app.core.dependencies import get_auth_service
from app.core.schema.auth import (
    EmployeeAuth,
    TokenResponse,
)
from app.service.auth import AuthService

router = APIRouter(
    prefix="/",
    tags=["auth"],
)

@router.post(
    "/login",
    response_model=TokenResponse,
)
async def login(
        data: EmployeeAuth,
        response: Response,
        service: AuthService = Depends(get_auth_service),
):
    access_, refresh_ = await service.login(data)
    response.set_cookie(
        key="refresh_token",
        value=refresh_,
        httponly=True,
        samesite="strict",
        secure=True, # на время без сертификата False
    )
    return {"access_token": access_, "token_type": "bearer"}

@router.post(
    "/refresh",
    response_model=TokenResponse,
)
async def refresh(
        response: Response,
        refresh_token: str | None = Cookie(None),
        service: AuthService = Depends(get_auth_service),
):
    ...
