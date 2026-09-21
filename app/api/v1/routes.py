from fastapi import APIRouter

from app.api.v1.endpoints.employee import router as employee_router

routers = APIRouter()

routers.include_router(employee_router)
