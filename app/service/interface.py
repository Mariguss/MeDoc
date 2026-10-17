from abc import (
    ABC,
    abstractmethod,
)

from pydantic import BaseModel

from app.repository.interface import ReadResult


class BaseServiceABC[DTOIn: BaseModel, DTOOut: BaseModel](ABC):
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
