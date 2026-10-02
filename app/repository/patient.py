from sqlalchemy.ext.asyncio import AsyncSession

from app.core.model.patient import Patient
from app.repository.base import BaseRepository


class PatientRepository(BaseRepository[Patient]):
    def __init__(
            self,
            session: AsyncSession,
    ) -> None:
        super().__init__(session, Patient)
