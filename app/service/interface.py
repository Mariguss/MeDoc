from abc import (
    ABC,
    abstractmethod,
)
from typing import (
    Generic,
    TypeVar,
)

from pydantic import BaseModel

from app.repository.interface import ReadResult

DTOIn = TypeVar("DTOIn", bound=BaseModel)
DTOOut = TypeVar("DTOOut", bound=BaseModel)


class BaseServiceABC(Generic[DTOIn, DTOOut], ABC):
    @abstractmethod
    async def get_list(self, **kwargs) -> ReadResult[DTOOut]:
        pass

    @abstractmethod
    async def get_by_id(self, id_: int) -> DTOOut:
        pass

    @abstractmethod
    async def add(self, schema: DTOIn) -> DTOOut:
        pass

    @abstractmethod
    async def patch(self, id_: int, schema: DTOIn) -> DTOOut:
        pass

    @abstractmethod
    async def remove_by_id(self, id_: int) -> None:
        pass
