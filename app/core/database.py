from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings


class Database:
    def __init__(self, url: str, echo: bool = False):
        self.engine = create_async_engine(
            url=url,
            echo=echo,
        )
        self.session = async_sessionmaker(
            bind=self.engine,
            expire_on_commit=False,
        )

    async def get_session(self) -> AsyncGenerator[AsyncSession]:
        async with self.session() as session:
            yield session


database = Database(
    url=settings.db.url,
    echo=settings.db.echo,
)
