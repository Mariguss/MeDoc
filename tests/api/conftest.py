from collections.abc import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.core.server import create_app


@pytest.fixture(scope="session")
def app() -> Generator[FastAPI]:
    app_ = create_app()
    yield app_


@pytest_asyncio.fixture(scope="function")
async def client(app: FastAPI) -> AsyncGenerator[AsyncClient]:
    async with AsyncClient(
        transport=ASGITransport(app), base_url="http://testserver/"
    ) as client_:
        yield client_

    app.dependency_overrides = {}
