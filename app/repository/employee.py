from typing import TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.model.employee import Employee
from app.repository.base import BaseRepository

T = TypeVar("T")

class EmployeeRepository(BaseRepository):
    def __init__(
            self,
            session: AsyncSession,
    ) -> None:
        super().__init__(session, Employee)

    async def get_by_login(self, login_: str) -> T | None:
        stmt = select(Employee).where(Employee.login == login_)
        data = await self.session.execute(stmt)
        return data.scalars().first()
