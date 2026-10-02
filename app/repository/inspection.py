import datetime
from typing import TypeVar

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.functions import func

from app.core.model import (
    InspectionDisease,
    Disease,
)
from app.core.model.inspection import Inspection, Status

T = TypeVar("T")

class InspectionRepository:
    def __init__(
            self,
            session: AsyncSession,
    ) -> None:
        self.session = session
        self._model = Inspection

    async def create(self, obj_data: Inspection) -> Inspection:
        self.session.add(obj_data)

        return obj_data

    async def update(self) -> None:
        await self.session.flush()

    async def read_by_id(self, id_: int) -> Inspection | None:
        stmt = select(self._model).where(self._model.id == id_)
        result = await self.session.execute(stmt)

        return result.scalars().first()

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

    async def get_inspection_count_by_day(
            self, status_: Status | None = Status.COMPLETED,
            start_date_: datetime.datetime | None = None,
            end_date_: datetime.datetime | None = None) -> list:

        date_label = func.date(Inspection.inspection_at).label("inspection_date")

        stmt = (
            select(
                date_label,
                func.count(Inspection.status).label("count")
            )
        )

        if status_ is not None:
            stmt = stmt.where(Inspection.status == status_)
        if start_date_ is not None:
            stmt = stmt.where(func.date(Inspection.inspection_at) >= start_date_)
        if end_date_ is not None:
            stmt = stmt.where(func.date(Inspection.inspection_at) <= end_date_)

        stmt = stmt.group_by(date_label).order_by(date_label.desc())

        result = await self.session.execute(stmt)

        return [
            {"date": row_.inspection_date, "count": row_.count}
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

    async def get_unique_patients_count_by_disease_ids(self, disease_ids_: list[int]) -> list:
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
