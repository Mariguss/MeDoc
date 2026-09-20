from typing import TypeVar

from fastapi import HTTPException, status


T = TypeVar("T")

class DuplicatedError(HTTPException):
    def __init__(self, detail: str | None= None, headers: dict[str, T] | None = None) -> None:
        super().__init__(status.HTTP_400_BAD_REQUEST, detail, headers)

class WrongCredentialsError(DuplicatedError):
    pass

class AuthError(HTTPException):
    def __init__(self, detail: str | None= None, headers: dict[str, T] | None = None) -> None:
        super().__init__(status.HTTP_403_FORBIDDEN, detail, headers)


class NotFoundError(HTTPException):
    def __init__(self, detail: str | None= None, headers: dict[str, T] | None = None) -> None:
        super().__init__(status.HTTP_404_NOT_FOUND, detail, headers)


class ValidationError(HTTPException):
    def __init__(self, detail: str | None= None, headers: dict[str, T] | None = None) -> None:
        super().__init__(status.HTTP_422_UNPROCESSABLE_ENTITY, detail, headers)
