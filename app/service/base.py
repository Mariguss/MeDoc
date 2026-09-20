# Для написания бизнес-логики (слой между repository и routes)
from typing import (
    Generic,
    TypeVar,
)


T = TypeVar("T")

class BaseService(Generic[T]):

    def __init__(self, repository) -> None:
        self._repository = repository

    async def get_list(self, schema: T | None = None) -> list[T]:
        return await self._repository.read_by_options(schema)

    async def get_by_id(self, id: int) -> T | None:
        item: T | None = await self._repository.read_by_id(id)
        if item is None:
            return None
        return item

    async def add(self, schema: T) -> T:
        return await self._repository.create(schema)

    async def patch(self, id: int, schema: T) -> T:
        return await self._repository.update(id, schema)

    async def remove_by_id(self, id: int) -> None:
        return await self._repository.delete_by_id(id)
