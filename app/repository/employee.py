from sqlalchemy.ext.asyncio import AsyncSession

from app.core.model.employee import Employee
from app.repository.base import BaseRepository


class EmployeeRepository(BaseRepository):
    def __init__(
            self,
            session: AsyncSession,
    ) -> None:
        super().__init__(session, Employee)
