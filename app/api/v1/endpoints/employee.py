# from fastapi import APIRouter, Depends
#
# from app.core.model.employee import Employee
# from app.service.employee import EmployeeService
#
# router = APIRouter(
#     prefix="/employee",
#     tags=["employee"],
# )
#
# @router.get("/{id}", response_model=Employee)
# async def get_employee(
#         id: int,
#         service: EmployeeService = Depends(EmployeeService()),
# ):
#     return await