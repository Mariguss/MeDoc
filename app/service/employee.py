from app.repository.employee import EmployeeRepository
from app.service.base import BaseService


class EmployeeService(BaseService):
    def __init__(self, repository: EmployeeRepository):
        super().__init__(repository)
