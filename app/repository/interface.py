from abc import (
    ABC,
    abstractmethod,
)
from typing import (
    Generic,
    TypeVar,
    TypedDict,
)

T = TypeVar("T")

class ReadResult(TypedDict, Generic[T]):
    founds: list[T]
    total_count: int

class BaseRepositoryABC(Generic[T], ABC):

    @abstractmethod
    async def read_by_options(
            self,
            page: int = 1,
            page_size: int = 10,
            ordering: str = "-id",
            **kwargs
    ) -> ReadResult[T]:
        ...

    @abstractmethod
    async def read_by_id(self, id: int) -> T | None:
        ...

    @abstractmethod
    async def create(self, schema: T) -> T:
        ...

    @abstractmethod
    async def update(self, id: int, schema: T) -> T | None:
        ...

    @abstractmethod
    async def delete_by_id(self, id: int) -> None:
        ...
