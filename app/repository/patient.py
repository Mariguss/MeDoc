from sqlalchemy.ext.asyncio import AsyncSession

from app.core.model.patient import Patient
from app.repository.base import BaseRepository


class PatientRepository(BaseRepository):
    def __init__(
            self,
            session: AsyncSession,
    ) -> None:
        super().__init__(session, Patient)
