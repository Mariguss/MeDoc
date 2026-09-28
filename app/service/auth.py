from http.client import HTTPException
from typing import TypeVar

from starlette import status

from app.core.exception import NotFoundError
from app.core.security import create_jwt_token
from app.repository.employee import EmployeeRepository
from app.service.base import BaseService
from app.util.hashing import verify_password

T = TypeVar('T')

class AuthService(BaseService):
    def __init__(self, repository: EmployeeRepository):
        super().__init__(repository)

    async def login(self, schema: T) -> tuple | None:
        try:
            obj = await self._repository.read_by_login(schema.login)
            if obj is None:
                raise NotFoundError(
                    detail=f"Запись с login {schema.login} не найдена."
                )
            if not verify_password(schema.password, obj.password):
                raise HTTPException(status.HTTP_401_UNAUTHORIZED) # смешение api и service логики?!!!

            token_data = {"sub": str(obj.id), "role": str(obj.role)}
            access_token_ = create_jwt_token(token_data)
            refresh_token_ = create_jwt_token(token_data, type_="refresh")
            return access_token_, refresh_token_

        except Exception as e:
            print("login", e)
            raise e
