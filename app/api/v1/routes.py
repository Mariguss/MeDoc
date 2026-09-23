from fastapi import APIRouter

from app.api.v1.endpoints.employee import router as employee_router
from app.api.v1.endpoints.patient import router as patient_router
from app.api.v1.endpoints.medicine import router as medicine_router
from app.api.v1.endpoints.inspection import router as inspection_router

routers = APIRouter()

routers.include_router(employee_router)
routers.include_router(patient_router)
routers.include_router(medicine_router)
routers.include_router(inspection_router)
