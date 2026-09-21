from abc import (
    ABC,
    abstractmethod,
)
from typing import (
    Generic,
    TypeVar,
)

from app.repository.interface import ReadResult

T = TypeVar("T")

class BaseServiceABC(Generic[T], ABC):

    @abstractmethod
    async def get_list(self, **kwargs) -> ReadResult[T]:
        ...

    @abstractmethod
    async def get_by_id(self, id_: int) -> T | None:
        ...

    @abstractmethod
    async def add(self, schema: T) -> T:
        ...

    @abstractmethod
    async def patch(self, id_: int, schema: T) -> T:
        ...

    @abstractmethod
    async def remove_by_id(self, id_: int) -> None:
        ...
