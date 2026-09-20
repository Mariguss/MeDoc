# Для написания бизнес-логики (слой между repository и routes)
from typing import (
    Generic,
    TypeVar,
)


T = TypeVar("T")

class BaseService(Generic[T]):

    def __init__(self, repository) -> None:
        self._repository = repository

    def get_list(self, schema: T | None = None) -> list[T]:
        return self._repository.read_by_options(schema)

    def get_by_id(self, id: int) -> T | None:
        item: T | None = self._repository.read_by_id(id)
        if item is None:
            return None
        return item

    def add(self, schema: T) -> T:
        return self._repository.create(schema)

    def patch(self, id: int, schema: T) -> T:
        return self._repository.update(id, schema)

    def remove_by_id(self, id: int) -> None:
        return self._repository.delete_by_id(id)
