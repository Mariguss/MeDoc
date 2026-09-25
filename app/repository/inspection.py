import datetime

from sqlalchemy import delete, select
from sqlalchemy.engine import row
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.functions import count, func

from app.core.model import InspectionDisease, Disease
from app.core.model.inspection import (
    Inspection,
    Status,
)
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

    async def get_inspection_count_by_day(self,status_: str | None = Status.COMPLETED, start: datetime.date | None = None, end: datetime.date | None = None) -> list:
        date_label = func.date(Inspection.inspection_at).label("inspection_date")

        stmt = (
            select(
                date_label,
                func.count(Inspection.status).label("count")
            )
        )

        if status_ is not None:
            stmt = stmt.where(Inspection.status == status_)
        if start is not None:
            stmt = stmt.where(func.date(Inspection.inspection_at) >= start)
        if end is not None:
            stmt = stmt.where(func.date(Inspection.inspection_at) <= end)

        stmt = stmt.group_by(date_label).order_by(date_label.desc())

        result = await self.session.execute(stmt)

        return [
            {"date": row_.inspection_date.isoformat(), "count": row_.count}
            for row_ in result.all()
        ]

    async def get_unique_patients_count_by_disease_id(self, disease_id_: int) -> int:
        distinct_patients = func.distinct(Inspection.patient_id)
        count_expression = func.count(distinct_patients)

        stmt = (
            select(count_expression)
            .join(
                InspectionDisease,
                Inspection.id == InspectionDisease.inspection_id,
            )
            .where(InspectionDisease.disease_id == disease_id_)
        )

        result = await self.session.execute(stmt)

        return result.scalar() or 0

    async def get_unique_patients_count_by_disease_ids(self, disease_ids_: int) -> list:
        distinct_patients = func.distinct(Inspection.patient_id)
        patients_count = func.count(distinct_patients).label("unique_patients_count")

        stmt = (
            select(
                Disease.id.label("disease_id"),
                Disease.name.label("disease_name"),
                patients_count,

            )
            .join(
                InspectionDisease,
                Inspection.id == InspectionDisease.inspection_id,
            )
            .join(
                Disease,
                InspectionDisease.disease_id == Disease.id,
            )
        )

        if disease_ids_ is not None:
            stmt = stmt.where(
                InspectionDisease.disease_id.in_(disease_ids_)
            )

        stmt = stmt.group_by(Disease.id, Disease.name).order_by(patients_count.desc())

        result = await self.session.execute(stmt)

        return [
            {
                "disease_id": row_.disease_id,
                "disease_name": row_.disease_name,
                "unique_patients_count": row_.unique_patients_count,
            }
            for row_ in result.all()
        ]