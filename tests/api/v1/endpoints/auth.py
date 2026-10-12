from unittest.mock import AsyncMock

import pytest
from httpx import AsyncClient

from app.core.dependencies import get_auth_service


@pytest.fixture(scope="function", autouse=True)
def mock_auth_service(app):
    service = AsyncMock()
    service.login.return_value = (
        "fake_access_token",
        "fake_refresh_token",
        "2026-10-12T17:06:00",
    )

    # Подменяем зависимость
    app.dependency_overrides[get_auth_service] = lambda: service
    return service


@pytest.mark.parametrize(
    'login_, password_',
    [
        ("testtest", "Aa123456!"),
    ]
)
@pytest.mark.asyncio
async def test_login_200(client: AsyncClient, login_, password_) -> None:
    user = {"login": login_, "password": password_}
    response = await client.post("/login", json=user)

    assert response.status_code == 200
    assert response.json()["access_token"] == "fake_access_token"
    assert "refresh_token" in response.cookies
    assert response.cookies["refresh_token"] == "fake_refresh_token"
    # print(response.json())
    # print(response.cookies)

@pytest.mark.parametrize(
    'login_, password_',
    [
        ("testtest", "!"),
        ("user", "!"),
        ("user", "Aa123456!"),
        ("", ""),
    ]
)
@pytest.mark.asyncio
async def test_login_422(client: AsyncClient, login_, password_) -> None:
    user = {"login": login_, "password": password_}
    response = await client.post("/login", json=user)

    assert response.status_code == 422

@pytest.mark.asyncio
async def test_login_without_login_422(client: AsyncClient) -> None:
    bad_user = {"password": "Aa123456!"}
    response = await client.post("/login", json=bad_user)

    assert response.status_code == 422

@pytest.mark.asyncio
async def test_login_without_password_422(client: AsyncClient) -> None:
    bad_user = {"login": "testtest"}
    response = await client.post("/login", json=bad_user)

    assert response.status_code == 422

@pytest.mark.asyncio
async def test_login_without_params_422(client: AsyncClient) -> None:
    bad_user = {}
    response = await client.post("/login", json=bad_user)

    assert response.status_code == 422

@pytest.mark.asyncio
async def test_login_wrong_params_422(client: AsyncClient) -> None:
    bad_user = {"email": "abc@e[ample.com", "password": "Aa123456!"}
    response = await client.post("/login", json=bad_user)

    assert response.status_code == 422
