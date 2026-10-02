from enum import Enum
from http.client import HTTPException
from typing import TypeVar

from starlette import status

from app.core.exception import NotFoundError
from app.core.security import create_jwt_token, decode_jwt
from app.repository.employee import EmployeeRepository
from app.service.base import BaseService
from app.util.hashing import verify_password

T = TypeVar('T')

class AuthService(BaseService):
    def __init__(self, repository: EmployeeRepository):
        super().__init__(repository)

    async def login(self, schema: T) -> tuple[str, str, str] | None:
        try:
            obj = await self._repository.get_by_login(schema.login)
            if obj is None:
                raise NotFoundError(
                    detail=f"Запись с login {schema.login} не найдена."
                )
            if not verify_password(schema.password_hash, obj.password_hash):
                raise HTTPException(status.HTTP_401_UNAUTHORIZED) # смешение api и service логики?!!!

            subject = {"sub": str(obj.id), "role": str(obj.role.value)}
            access_token_, expire_at = create_jwt_token(subject)
            refresh_token_, _ = create_jwt_token(subject, type_="refresh")
            return access_token_, refresh_token_, expire_at

        except Exception as e:
            print("login", e)
            raise e

    async def refresh(self, refresh_token_: str) -> tuple[str, str] | None:
        payload = decode_jwt(refresh_token_)
        if payload is None:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED)

        if payload.get("type") != "refresh":
            raise HTTPException(status.HTTP_401_UNAUTHORIZED)

        user_id = payload.get("sub")
        user_role = payload.get("role")

        if not await self._repository.exist(user_id):
            raise HTTPException(status.HTTP_403_FORBIDDEN)

        subject = {
            "sub": user_id,
            "role": user_role,
        }

        new_access_token = create_jwt_token(subject, type_="access")

        return new_access_token
