from typing import Any, AsyncGenerator, Generator

import pytest
import pytest_asyncio
from core.server import create_app
from fastapi import FastAPI
from httpx import AsyncClient

from app.core.database import database


@pytest.fixture(scope="session")
def app() -> Generator[FastAPI | None]:
    """
    Create a new FastAPI app
    """
    app = create_app()

    yield app


@pytest_asyncio.fixture(scope="function")
async def client(app: FastAPI, db_session) -> AsyncGenerator[AsyncClient, Any]:
    """
    Create a new FastAPI AsyncClient
    """

    async def _get_session():
        return db_session

    app.dependency_overrides[database.get_session()] = _get_session

    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
