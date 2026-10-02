# Для написания бизнес-логики (слой между repository и routes)
from typing import (
    Generic,
    TypeVar,
    cast,
    Any,
)

from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError

from app.core.exception import (
    DuplicatedError,
    RelationshipViolationError,
    NotFoundError,
)
from app.core.model import Base
from app.repository.interface import ReadResult

DTOIn = TypeVar("DTOIn", bound=BaseModel)
DTOOut = TypeVar("DTOOut", bound=BaseModel)
ModelT = TypeVar("ModelT", bound=Base)


class BaseService(Generic[DTOIn, DTOOut]):
    def __init__(self, repository, model_class: type[Base]) -> None:
        self._repository = repository
        self._model_class = model_class

    async def get_list(self, **kwargs) -> ReadResult[DTOIn]:
        return await self._repository.read_by_options(**kwargs)

    async def get_by_id(self, id_: int) -> DTOOut:
        obj = await self._repository.read_by_id(id_)
        if obj is None:
            raise NotFoundError(detail=f"Запись с ID {id_} не найдена.")
        return cast(DTOOut, cast(Any, obj))

    async def add(self, schema: DTOIn) -> DTOOut:
        try:
            db_obj = self._model_class(**schema.model_dump())

            obj = await self._repository.create(db_obj)
            await self._repository.session.commit()
            await self._repository.session.refresh(obj)
            return cast(DTOOut, cast(Any, obj))
        except IntegrityError:
            await self._repository.session.rollback()
            raise DuplicatedError(
                detail="Запись с такими уникальными атрибутами уже существует."
            )

    async def patch(self, id_: int, schema: DTOIn) -> DTOOut:
        try:
            obj = await self._repository.read_by_id(id_)
            if obj is None:
                raise NotFoundError(detail=f"Запись с ID {id_} не найдена.")
            update_data = schema.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(obj, key, value)

            await self._repository.session.update()

            await self._repository.session.commit()
            await self._repository.session.refresh(obj)

            return cast(DTOOut, cast(Any, obj))
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
