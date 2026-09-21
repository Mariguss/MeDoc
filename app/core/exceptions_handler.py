from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.exception import (
    AuthError,
    DuplicatedError,
    NotFoundError,
    RelationshipViolationError,
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
