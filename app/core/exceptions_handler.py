from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.exception import (
    AccessDeniedError,
    AuthError,
    DuplicatedError,
    NewException,
    NotFoundError,
    RelationshipViolationError,
    UnauthorizedError,
    ValidationError,
)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(NotFoundError)
    async def _(_: Request, exc: NotFoundError) -> JSONResponse:
        return JSONResponse(status_code=404, content={"detail": exc.detail})

    @app.exception_handler(DuplicatedError)
    async def _(_: Request, exc: DuplicatedError) -> JSONResponse:
        return JSONResponse(status_code=409, content={"detail": exc.detail})

    @app.exception_handler(RelationshipViolationError)
    async def _(_: Request, exc: RelationshipViolationError) -> JSONResponse:
        return JSONResponse(status_code=409, content={"detail": exc.detail})

    @app.exception_handler(AuthError)
    async def _(_: Request, exc: AuthError) -> JSONResponse:
        return JSONResponse(status_code=401, content={"detail": exc.detail})

    @app.exception_handler(ValidationError)
    async def _(_: Request, exc: ValidationError) -> JSONResponse:
        return JSONResponse(status_code=422, content={"detail": exc.detail})

    @app.exception_handler(AccessDeniedError)
    async def _(_: Request, exc: AccessDeniedError) -> JSONResponse:
        return JSONResponse(status_code=403, content={"detail": exc.detail})

    @app.exception_handler(UnauthorizedError)
    async def _(_: Request, exc: UnauthorizedError) -> JSONResponse:
        return JSONResponse(status_code=401, content={"detail": exc.detail})

    @app.exception_handler(NewException)
    async def _(_: Request, exc: NewException) -> JSONResponse:
        return JSONResponse(status_code=500, content={"detail": "Внутренняя ошибка"})
