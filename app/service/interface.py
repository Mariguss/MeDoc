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
    def get_list(self, schema: T | None = None) -> list[T]:
        ...

    @abstractmethod
    def get_by_id(self, id: int) -> T | None:
        ...

    @abstractmethod
    def add(self, schema: T) -> T:
        ...

    @abstractmethod
    def patch(self, id: int, schema: T) -> T:
        ...

    @abstractmethod
    def remove_by_id(self, id: int) -> None:
        ...
