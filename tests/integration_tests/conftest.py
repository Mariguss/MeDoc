from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.database import database
from app.core.dependencies import (
    auth_bearer,
    get_current_user_id,
    get_current_user_role,
)
from app.core.model import Base
from app.core.server import create_app

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
test_engine = create_async_engine(
    TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = async_sessionmaker(
    autocommit=False, autoflush=False, bind=test_engine
)


@pytest_asyncio.fixture(scope="function")
async def session():
    # Создаем таблицы в тестовой БД перед каждым тестом
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        # Открываем асинтек-соединение и транзакцию
    async with test_engine.connect() as connection:
        transaction = await connection.begin()

        # Создаем изолированную асинхронную сессию
        async with TestingSessionLocal(bind=connection) as session_:
            yield session_

            # После теста полностью откатываем транзакцию
            await transaction.rollback()

        # Очищаем структуру таблиц после завершения теста
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def app(session) -> AsyncGenerator[FastAPI]:
    app_ = create_app()
    app_.dependency_overrides[database.get_session] = lambda: session
    yield app_
    app_.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="function")
async def client(app: FastAPI) -> AsyncGenerator[AsyncClient]:
    async with AsyncClient(
        transport=ASGITransport(app), base_url="http://testserver/"
    ) as client_:
        yield client_


@pytest.fixture(scope="function")
def as_doctor(app):
    app.dependency_overrides[auth_bearer] = lambda: 1
    app.dependency_overrides[get_current_user_role] = lambda: "doctor"
    app.dependency_overrides[get_current_user_id] = lambda: 1
    yield
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def as_admin(app):
    app.dependency_overrides[auth_bearer] = lambda: 1
    app.dependency_overrides[get_current_user_role] = lambda: "admin"
    app.dependency_overrides[get_current_user_id] = lambda: 1
    yield
    app.dependency_overrides.clear()
