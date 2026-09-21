from sqlalchemy.ext.asyncio import AsyncSession

from app.core.model.prescription import Prescription
from app.repository.base import BaseRepository


class PrescriptionRepository(BaseRepository):
    def __init__(
            self,
            session: AsyncSession,
    ) -> None:
        super().__init__(session, Prescription)
