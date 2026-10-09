from abc import (
    ABC,
    abstractmethod,
)
from typing import (
    Generic,
    TypedDict,
    TypeVar,
)

T = TypeVar("T")


class ReadResult(TypedDict, Generic[T]):
    founds: list[T]
    total_count: int


class BaseRepositoryABC(Generic[T], ABC):
    @abstractmethod
    def _build_stmt_with_filters(self, stmt, **kwargs):
        pass

    @abstractmethod
    async def read_by_options(
        self,
        page: int = 1,
        page_size: int = 10,
        ordering: str = "-id",
        **kwargs,
    ) -> ReadResult[T]:
        pass

    @abstractmethod
    async def read_by_id(self, id_: int) -> T | None:
        pass

    @abstractmethod
    async def exist(self, id_: int) -> bool:
        pass

    @abstractmethod
    async def all_exist(self, ids_: list[int]) -> bool:
        pass

    @abstractmethod
    async def create(self, schema: T) -> T:
        pass

    @abstractmethod
    async def create_all(self, objs: list[T]) -> None:
        pass

    @abstractmethod
    async def update(self, id_: int) -> None:
        pass

    @abstractmethod
    async def delete_by_id(self, id_: int) -> None:
        pass

    @abstractmethod
    async def delete_all_by_id(self, ids_: list[int]) -> None:
        pass
