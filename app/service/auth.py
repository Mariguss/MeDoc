from fastapi import HTTPException
from starlette import status

from app.core.exception import NotFoundError
from app.core.model import Employee
from app.core.schema.auth import EmployeeAuth
from app.core.security import (
    create_jwt_token,
    decode_jwt,
)
from app.repository.employee import EmployeeRepository
from app.service.base import BaseService
from app.util.hashing import verify_password


class AuthService():
    def __init__(self, repository: EmployeeRepository):
        self._repository = repository

    async def login(self, schema: EmployeeAuth) -> tuple[str, str, str]:
        try:
            obj = await self._repository.get_by_login(schema.login)
            if obj is None:
                raise NotFoundError(
                    detail=f"Запись с login {schema.login} не найдена."
                )
            if not verify_password(schema.password, obj.password_hash):
                raise HTTPException(status.HTTP_401_UNAUTHORIZED) # смешение api и service логики?!!!

            subject = {"sub": str(obj.id), "role": str(obj.role.value)}
            access_token_, expire_at = create_jwt_token(subject)
            refresh_token_, _ = create_jwt_token(subject, type_="refresh")
            return access_token_, refresh_token_, expire_at

        except Exception as e:
            print("login", e)
            raise e

    async def refresh(self, refresh_token_: str) -> tuple[str, str]:
        payload = decode_jwt(refresh_token_)
        if payload is None:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED)

        if payload.get("type") != "refresh":
            raise HTTPException(status.HTTP_401_UNAUTHORIZED)

        user_id: int | None = payload.get("sub")
        user_role: str | None = payload.get("role")

        if user_id is None or user_role is None:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED)

        if not await self._repository.exist(user_id):
            raise HTTPException(status.HTTP_403_FORBIDDEN)

        subject = {
            "sub": user_id,
            "role": user_role,
        }

        new_access_token = create_jwt_token(subject, type_="access")

        return new_access_token
