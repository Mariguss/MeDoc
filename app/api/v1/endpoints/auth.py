from fastapi import (
    APIRouter,
    Depends,
    Response,
    Cookie, HTTPException,
)
from starlette import status

from app.core.dependencies import get_auth_service
from app.core.schema.auth import (
    EmployeeAuth,
    TokenResponse,
)
from app.service.auth import AuthService

router = APIRouter(
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
    access_, refresh_, expire_at = await service.login(data)
    response.set_cookie(
        key="refresh_token",
        value=refresh_,
        httponly=True,
        samesite="strict",
        secure=False, # на время без сертификата False
    )
    return {
        "access_token": access_,
        "token_type": "bearer",
        "expires_at": expire_at,
    }

@router.post(
    "/refresh",
    response_model=TokenResponse,
)
async def refresh(
        refresh_token: str | None = Cookie(None),
        service: AuthService = Depends(get_auth_service),
):
    if not refresh_token:
        raise HTTPException(
            detail="Сессия истекла. Пожалуйста, авторизуйтесь заново",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )
    new_access, new_expire = await service.refresh(refresh_token)

    return {
        "access_token": new_access,
        "token_type": "bearer",
        "expires_at": new_expire,
    }
