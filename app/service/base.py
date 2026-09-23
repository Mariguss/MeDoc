# Для написания бизнес-логики (слой между repository и routes)
from typing import (
    Generic,
    TypeVar,
)

from sqlalchemy.exc import IntegrityError

from app.core.exception import (
    DuplicatedError,
    RelationshipViolationError,
    NotFoundError,
)
from app.repository.interface import ReadResult

T = TypeVar("T")

class BaseService(Generic[T]):

    def __init__(self, repository) -> None:
        self._repository = repository

    async def get_list(self, **kwargs) -> ReadResult[T]:
        return await self._repository.read_by_options(**kwargs)

    async def get_by_id(self, id_: int) -> T:
        obj = await self._repository.read_by_id(id_)
        if obj is None:
            raise NotFoundError(
                detail=f"Запись с ID {id_} не найдена."
            )
        return obj

    async def add(self, schema: T) -> T:
        try:
            obj = await self._repository.create(schema)
            await self._repository.session.commit()
            await self._repository.session.refresh(obj)
            return obj
        except IntegrityError:
            await self._repository.session.rollback()
            raise DuplicatedError(
                detail="Запись с такими уникальными атрибутами уже существует."
            )

    async def patch(self, id_: int, schema: T) -> T:
        try:
            obj = await self._repository.update(id_, schema)
            if obj is None:
                raise NotFoundError(
                    detail=f"Запись с ID {id_} не найдена."
                )
            await self._repository.session.commit()
            await self._repository.session.refresh(obj)
            return obj
        except IntegrityError:
            await self._repository.session.rollback()
            raise DuplicatedError(
                detail="Обновление не выполнено из-за нарушения уникальности"
            )

    async def remove_by_id(self, id_: int) -> None:
        try:
            await self._repository.delete_by_id(id_)
            await self._repository.session.commit()
        except IntegrityError:
            await self._repository.session.rollback()
            raise RelationshipViolationError(
                detail="Невозможно удалить запись: на неё есть ссылки в других таблицах."
            )
