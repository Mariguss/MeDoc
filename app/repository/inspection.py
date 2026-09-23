from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.model import InspectionDisease
from app.core.model.inspection import Inspection
from app.repository.base import BaseRepository


class InspectionRepository(BaseRepository):
    def __init__(
            self,
            session: AsyncSession,
    ) -> None:
        super().__init__(session, Inspection)

    async def update_diseases(self, inspection_id: int, disease_ids: list[int]) -> None:
        await self.session.execute(
            delete(InspectionDisease)
            .where(InspectionDisease.inspection_id == inspection_id)
        )

        for d_id in disease_ids:
            link = InspectionDisease(
                inspection_id=inspection_id,
                disease_id=d_id,
            )
            self.session.add(link)
