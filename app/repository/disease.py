from sqlalchemy.ext.asyncio import AsyncSession

from app.core.model.disease import Disease
from app.repository.base import BaseRepository


class DiseaseRepository(BaseRepository[Disease]):
    def __init__(
            self,
            session: AsyncSession,
    ) -> None:
        super().__init__(session, Disease)
