from unittest.mock import AsyncMock

import pytest
from httpx import AsyncClient

from app.core.dependencies import get_auth_service


# Мок для сервиса авторизации живет только в этом файле!
@pytest.fixture(scope="function", autouse=True)
def mock_auth_service(app):
    service = AsyncMock()
    service.login.return_value = (
        "fake_access_token",
        "fake_refresh_token",
        "2026-10-12T17:06:00",
    )

    # Подменяем зависимость прямо здесь
    app.dependency_overrides[get_auth_service] = lambda: service
    return service


@pytest.mark.asyncio
async def test_login(client: AsyncClient) -> None:
    # Этот клиент автоматически подхватит подмену, сделанную выше в блоке autouse
    user = {"login": "testtest", "password": "Aa123456!"}
    response = await client.post("/login", json=user)

    assert response.status_code == 200
    assert response.json()["access_token"] == "fake_access_token"
    print(response.json())