from app.core.schema.employee import EmployeeCreate
from app.repository.employee import EmployeeRepository


class EmployeeService:
    def __init__(self, repository: EmployeeRepository):
        super().__init__(repository)
