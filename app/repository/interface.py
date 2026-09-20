from abc import (
    ABC,
    abstractmethod,
)
from typing import (
    Generic,
    TypeVar,
)

T = TypeVar("T")

class BaseRepositoryABC(Generic[T], ABC):

    @abstractmethod
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

    @abstractmethod
    async def read_by_id(self, id: int) -> T | None:
        ...

    @abstractmethod
    async def create(self, schema: T) -> T:
        ...

    @abstractmethod
    async def update(self, id: int, schema: T) -> T:
        ...

    @abstractmethod
    async def delete_by_id(self, id: int) -> None:
        ...
