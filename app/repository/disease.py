from contextlib import AbstractAsyncContextManager
from typing import Callable

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.model.disease import Disease
from app.repository.base import BaseRepository


class DiseaseRepository(BaseRepository):
    def __init__(
            self,
            session_factory: Callable[..., AbstractAsyncContextManager[AsyncSession]],
    ) -> None:
        super().__init__(session_factory, Disease)
