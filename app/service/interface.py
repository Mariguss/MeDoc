from abc import (
    ABC,
    abstractmethod,
)
from typing import (
    Generic,
    TypeVar,
)

T = TypeVar("T")

class BaseServiceABC(Generic[T], ABC):

    @abstractmethod
    async def get_list(self, schema: T | None = None) -> list[T]:
        ...

    @abstractmethod
    async def get_by_id(self, id: int) -> T | None:
        ...

    @abstractmethod
    async def add(self, schema: T) -> T:
        ...

    @abstractmethod
    async def patch(self, id: int, schema: T) -> T:
        ...

    @abstractmethod
    async def remove_by_id(self, id: int) -> None:
        ...
