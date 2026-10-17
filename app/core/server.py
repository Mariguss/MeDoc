from fastapi import FastAPI

from app.api.v1.routes import routers
from app.core.exceptions_handler import register_exception_handlers


def create_app() -> FastAPI:
    app_ = FastAPI()
    register_exception_handlers(app_)
    app_.include_router(routers)
    return app_


app = create_app()
