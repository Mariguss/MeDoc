from typing import (
    Generic,
    TypeVar,
    cast,
)

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.functions import func

from app.core.exception import NotFoundError
from app.repository.interface import ReadResult

T = TypeVar("T")

class BaseRepository(Generic[T]):

    def __init__(
            self,
            session: AsyncSession,
            model: T,
    ) -> None:
        self.session = session
        self._model = model

    def _build_stmt_with_filters(self, stmt, **kwargs):
        """
        Функция для построения выражения с фильтрами, уникальными для каждой сущности
        :param stmt: select выражение
        :param kwargs: словарь с фильтрами
        :return: выражение с добавленными фильтрами
        """
        if kwargs:
            for k, v in kwargs.items():
                col = getattr(self._model, k, None)
                if col is not None:
                    stmt = stmt.where(col == v)
        return stmt

    async def read_by_options(
            self,
            page: int = 1,
            page_size: int = 10,
            ordering: str = "-id",
            **kwargs,
    ) -> ReadResult[T]:
        stmt = select(self._model)
        stmt = self._build_stmt_with_filters(stmt, **kwargs)

        order_field = ordering.lstrip("-")
        order_col = getattr(self._model, order_field, None) or self._model.id
        stmt = stmt.order_by(
            order_col.desc() if ordering.startswith("-") else order_col.asc(),
        )

        stmt_paginated = stmt.limit(page_size).offset((page - 1) * page_size)
        results = await self.session.execute(stmt_paginated)
        founds = results.scalars().unique().all()
        founds: list[T] = cast(list[T], founds)

        count_stmt = select(func.count()).select_from(self._model)
        count_stmt = self._build_stmt_with_filters(count_stmt, **kwargs)
        total_count = (await self.session.execute(count_stmt)).scalar() or 0

        return {"founds": founds, "total_count": total_count}

    async def read_by_id(self, id_: int) -> T | None:
        stmt = select(self._model).where(self._model.id == id_)
        result = await self.session.execute(stmt)

        return result.scalars().first()

    async def exist(self, id_: int) -> bool:
        stmt = select(self._model).where(self._model.id == id_)
        result = await self.session.execute(stmt)
        obj = result.scalars().first()
        print("obj", obj)
        if obj is not None:
            return True
        return False

    async def all_exist(self, ids_: list[int]) -> bool:
        for id_ in ids_:
            if await self.exist(id_):
                continue
            else:
                return False
        return True

    async def create(self, schema: T) -> T:
        obj = self._model(**schema.model_dump(exclude_none=True))
        self.session.add(obj)

        return obj

    async def create_all(self, objs: list[T]) -> None:
        for obj in objs:
            self.session.add(obj)

    async def update(self, id_: int, schema: T) -> T | None:
        stmt = select(self._model).where(self._model.id == id_)
        result = await self.session.execute(stmt)
        obj = result.scalars().first()

        if obj is None:
            return None

        data = schema.model_dump(exclude_unset=True)
        for k, v in data.items():
            setattr(obj, k, v)

        return obj

    async def update_all(self, objs: list[T]) -> bool:
        for obj in objs:
            id_ = obj.id
            flag = await self.update(id_, obj)
            if flag is None:
                return False
        return True

    async def delete_by_id(self, id_: int) -> None:
        stmt = select(self._model).where(self._model.id == id_)
        result = await self.session.execute(stmt)
        obj = result.scalars().first()

        if obj is None:
            raise NotFoundError(detail=f"Record with this id({id_}) does not exist.")

        await self.session.delete(obj)

    async def delete_all_by_id(self, ids_: list[int]) -> None:
        for id_ in ids_:
            await self.delete_by_id(id_)

