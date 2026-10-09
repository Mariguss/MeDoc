from fastapi import FastAPI

from app.api.v1.routes import routers
from app.core.exceptions_handler import register_exception_handlers


def create_app():
    app = FastAPI()
    register_exception_handlers(app)
    app.include_router(routers)
    return app


app = create_app()
