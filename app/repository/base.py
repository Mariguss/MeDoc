from contextlib import AbstractAsyncContextManager
from typing import (
    Generic,
    TypeVar,
    Callable,
)

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exception import (
    DuplicatedError,
    NotFoundError,
)

T = TypeVar("T")

class BaseRepositoryABC(Generic[T]):

    def __init__(
            self,
            session_factory: Callable[..., AbstractAsyncContextManager[AsyncSession]],
            model: T,
    ) -> None:
        self._session_factory = session_factory
        self._model = model

    async def read_by_options(
            self,
            schema: T | None = None,
            page: int = 1,
            page_size: int = 10,
            ordering: str = "-id",
    ) -> dict:
        """
            Возвращает:
            {
                "founds": List[T],
                "total_count": int,
            }
        """
        ...

    async def read_by_id(self, id: int) -> T | None:
        async with self._session_factory() as session:
            result = await session.execute(self._model.get(id=id))

        return result.scalars().first()


    async def create(self, schema: T) -> T:
        async with self._session_factory() as session:
            obj = self._model(schema.model_dump(exclude_none=True))
            try:
                session.add(obj)
                await session.commit()
            except IntegrityError:
                await session.rollback()
                raise DuplicatedError(
                    detail="Record with this unique attribute already exists."
                )
            return obj

    async def update(self, id: int, schema: T) -> T:
        async with self._session_factory() as session:
            result = await session.execute(self._model.get(id=id))
            obj = result.scalars().first()
            if obj is None:
                raise NotFoundError(detail=f"Record with this id({id}) does not exist.")

            data = schema.model_dump(exclude_none=True)
            for k, v in data.items():
                setattr(obj, k, v)

            await session.commit()
            await session.refresh(obj)
            return obj

    async def delete_by_id(self, id: int) -> None:
        async with self._session_factory() as session:
            result = await session.execute(self._model.get(id=id))
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
