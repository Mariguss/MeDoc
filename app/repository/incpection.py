from contextlib import AbstractAsyncContextManager
from typing import Callable

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.model.inspection import Inspection
from app.repository.base import BaseRepository


class InspectionRepository(BaseRepository):
    def __init__(
            self,
            session_factory: Callable[..., AbstractAsyncContextManager[AsyncSession]],
    ) -> None:
        super().__init__(session_factory, Inspection)
