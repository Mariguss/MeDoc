from contextlib import AbstractAsyncContextManager
from typing import (
    Generic,
    TypeVar,
    Callable,
    cast,
)

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.functions import func

from app.core.exception import (
    DuplicatedError,
    NotFoundError,
)
from app.repository.interface import ReadResult

T = TypeVar("T")

class BaseRepository(Generic[T]):

    def __init__(
            self,
            session_factory: Callable[..., AbstractAsyncContextManager[AsyncSession]],
            model: T,
    ) -> None:
        self._session_factory = session_factory
        self._model = model

    def _build_stmt_with_filters(self, stmt, **kwargs):
        """
        Функция для построения выражения с фильтрами, уникальными для каждой сущности
        :param stmt: select выражение
        :param kwargs: словарь с фильтрами
        :return: выражение с добавленными фильтрами
        """
        return stmt

    async def read_by_options(
            self,
            page: int = 1,
            page_size: int = 10,
            ordering: str = "-id",
            **kwargs,
    ) -> ReadResult[T]:
        async with self._session_factory() as session:
            stmt = select(self._model)
            stmt = self._build_stmt_with_filters(stmt, **kwargs)

            order_field = ordering.lstrip("-")
            order_col = getattr(self._model, order_field, None) or self._model.id
            stmt = stmt.order_by(
                order_col.desc() if ordering.startswith("-") else order_col.asc(),
            )

            stmt_paginated = stmt.limit(page_size).offset((page - 1) * page_size)
            results = await session.execute(stmt_paginated)
            founds = results.scalars().unique().all()
            founds: list[T] = cast(list[T], founds)

            count_stmt = select(func.count()).select_from(self._model)
            count_stmt = self._build_stmt_with_filters(count_stmt, **kwargs)
            total_count = (await session.execute(count_stmt)).scalar() or 0

        return {"founds": founds, "total_count": total_count}

    async def read_by_id(self, id: int) -> T | None:
        async with self._session_factory() as session:
            stmt = select(self._model).where(self._model.id == id)
            result = await session.execute(stmt)

        return result.scalars().first()

    async def create(self, schema: T) -> T:
        async with self._session_factory() as session:
            obj = self._model(schema.model_dump(exclude_none=True))
            try:
                session.add(obj)
                await session.commit()
                await session.refresh(obj)
            except IntegrityError:
                await session.rollback()
                raise DuplicatedError(
                    detail="Record with this unique attribute already exists."
                )
            return obj

    async def update(self, id: int, schema: T) -> T | None:
        async with self._session_factory() as session:
            stmt = select(self._model).where(self._model.id == id)
            result = await session.execute(stmt)
            obj = result.scalars().first()
            if obj is None:
                return None

            data = schema.model_dump(exclude_none=True)
            for k, v in data.items():
                setattr(obj, k, v)

            await session.commit()
            await session.refresh(obj)
            return obj

    async def delete_by_id(self, id: int) -> None:
        async with self._session_factory() as session:
            stmt = select(self._model).where(self._model.id == id)
            result = await session.execute(stmt)
            obj = result.scalars().first()
            if obj is None:
                raise NotFoundError(detail=f"Record with this id({id}) does not exist.")
            try:
                await session.delete(obj)
                await session.commit()
            except IntegrityError:
                await session.rollback()
                raise DuplicatedError(
                    detail="Заменить на исключение для случая невозможности удаления из-за связанности с другой записью"
                )
