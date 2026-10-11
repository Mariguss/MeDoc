from collections.abc import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.core.database import database
from app.core.server import create_app


@pytest.fixture(scope="session")
def app() -> Generator[FastAPI]:
    """
    Create a new FastAPI app
    """
    app = create_app()

    yield app


@pytest_asyncio.fixture(scope="function")
async def client(app: FastAPI, db_session) -> AsyncGenerator[AsyncClient]:
    """
    Create a new FastAPI AsyncClient
    """

    async def _get_session():
        return db_session

    app.dependency_overrides[database.get_session] = _get_session

    async with AsyncClient(
        transport=ASGITransport(app), base_url="http://test"
    ) as client:
        yield client

    app.dependency_overrides.pop(database.get_session, None)
