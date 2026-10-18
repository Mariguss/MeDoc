from typing import Any
from unittest.mock import AsyncMock

import pytest
from httpx import AsyncClient

from app.core.dependencies import (
    auth_bearer,
    get_employee_service,
)
from app.core.exception import (
    DuplicatedError,
    NotFoundError,
    RelationshipViolationError,
)
from app.core.exceptions_handler import register_exception_handlers
from app.core.schema.employee import EmployeeUpdate

payload_get = {
    "id": 1,
    "login": "fake_login1",
    "name": "Иванов Иван Иванович",
    "role": "doctor",
    "speciality": "ЛОР"
}

payload_add = {
    "login": "fake_login2",
    "name": "Новый Работник",
    "role": "admin",
    "speciality": "ЛОР",
    "password": "SecurePassword1!"
}

patch_name_payload = {"name": "Петров Иван Иванович"}

payload_patch = {**payload_get, **patch_name_payload}

payload_pagination: dict[str, Any] = {
    "founds": [payload_get],
    "total_count": 15,
}

@pytest.fixture(scope="function", autouse=True)
def mock_employee_service(app):
    register_exception_handlers(app)
    service = AsyncMock()

    # Подменяем зависимость
    app.dependency_overrides[get_employee_service] = lambda: service
    app.dependency_overrides[auth_bearer] = lambda: {"role": "admin"}

    service.get_by_id.return_value = payload_get

    service.add.return_value = {"id": 2, **payload_add}

    service.patch.return_value = payload_patch

    service.get_list.return_value = payload_pagination

    service.remove_by_id.return_value = True

    yield service

    app.dependency_overrides.clear()


# get /employee/1 200
@pytest.mark.asyncio
async def test_get_employee(client: AsyncClient, mock_employee_service: AsyncMock) -> None:
    response = await client.get("/employee/1")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["login"] == "fake_login1"
    assert data["name"] == "Иванов Иван Иванович"
    assert data["role"] == "doctor"
    assert data["speciality"] == "ЛОР"

    # Проверяем, что эндпоинт передал в сервис правильный ID (целое число, а не строку)
    mock_employee_service.get_by_id.assert_called_once_with(1)

# get /employee/1 404
@pytest.mark.asyncio
async def test_get_employee_not_found(client: AsyncClient, mock_employee_service: AsyncMock) -> None:
    mock_employee_service.get_by_id.side_effect = NotFoundError(
        detail="Работник не найден"
    )

    response = await client.get("/employee/1")

    assert response.status_code == 404
    assert response.json()["detail"] == "Работник не найден"
    mock_employee_service.get_by_id.assert_called_once_with(1)

# get /employee/{str} 422
@pytest.mark.asyncio
async def test_get_employee_invalid_id_type(client: AsyncClient, mock_employee_service: AsyncMock) -> None:
    response = await client.get("/employee/not-a-number")

    assert response.status_code == 422
    # Сервис вообще не должен вызываться, так как валидация упала на уровне FastAPI
    mock_employee_service.get_by_id.assert_not_called()

# post /employee/ 201
@pytest.mark.asyncio
async def test_create_employee_success(
    client: AsyncClient, mock_employee_service: AsyncMock
) -> None:
    response = await client.post("/employee/", json=payload_add)

    assert response.status_code == 201
    assert response.json()["id"] == 2
    mock_employee_service.add.assert_called_once()

# post /employee/ 422
@pytest.mark.asyncio
async def test_create_employee_invalid_body(client: AsyncClient, mock_employee_service: AsyncMock) -> None:
    response = await client.post("/employee/", json={})

    assert response.status_code == 422
    assert "detail" in response.json()
    mock_employee_service.add.assert_not_called()

# post /employee/ 409 (Дубликат, например, по номеру телефона)
@pytest.mark.asyncio
async def test_create_employee_duplicate(
    client: AsyncClient, mock_employee_service: AsyncMock
) -> None:
    mock_employee_service.add.side_effect = DuplicatedError(
        detail="Запись с такими уникальными атрибутами уже существует."
    )

    response = await client.post("/employee/", json=payload_add)

    assert response.status_code == 409
    assert "уникальными атрибутами" in response.json()["detail"]

# patch /employee/1 200
@pytest.mark.asyncio
async def test_update_employee_success(
    client: AsyncClient, mock_employee_service: AsyncMock
) -> None:
    response = await client.patch("/employee/1", json=patch_name_payload)

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["name"] == "Петров Иван Иванович"

    mock_employee_service.patch.assert_called_once_with(
        1,
        EmployeeUpdate(login=None, name="Петров Иван Иванович", role=None, speciality=None)
    )

# patch /employee/1 404
@pytest.mark.asyncio
async def test_update_employee_not_found(
    client: AsyncClient, mock_employee_service: AsyncMock
) -> None:
    # Имитируем, что сервис выбросил NotFoundError
    mock_employee_service.patch.side_effect = NotFoundError(detail="Запись с ID 1 не найдена.")

    response = await client.patch("/employee/1", json=patch_name_payload)

    assert response.status_code == 404
    assert response.json()["detail"] == "Запись с ID 1 не найдена."

# get /employee/ 200
@pytest.mark.asyncio
async def test_get_employees_list_pagination(
    client: AsyncClient, mock_employee_service: AsyncMock
) -> None:
    response = await client.get(
        "/employee/", params={"page": 1, "page_size": 1, "ordering": "name"}
    )

    assert response.status_code == 200
    data = response.json()

    # Проверяем структуру PaginatedResponse
    assert "founds" in data
    assert len(data["founds"]) == len(payload_pagination["founds"])
    assert data["founds"][0]["name"] == payload_get.get('name')
    assert data["total_count"] == payload_pagination.get('total_count')

    mock_employee_service.get_list.assert_called_once_with(
        page=1, page_size=1, ordering="name"
    )

# delete /employee/1 204
@pytest.mark.asyncio
async def test_delete_employee_success(client: AsyncClient, mock_employee_service: AsyncMock) -> None:
    response = await client.delete("/employee/1")

    assert response.status_code == 204
    assert response.content == b""
    mock_employee_service.remove_by_id.assert_called_once_with(1)

# delete /employee/1 404
@pytest.mark.asyncio
async def test_delete_employee_not_found(
    client: AsyncClient, mock_employee_service: AsyncMock
) -> None:
    mock_employee_service.remove_by_id.side_effect = NotFoundError(detail="Запись с таким id не найдена")

    response = await client.delete("/employee/1")

    assert response.status_code == 404
    assert response.json()["detail"] == "Запись с таким id не найдена"

# delete /employee/1 409 (Есть привязанные данные в других таблицах)
@pytest.mark.asyncio
async def test_delete_employee_relationship_violation(
    client: AsyncClient, mock_employee_service: AsyncMock
) -> None:
    mock_employee_service.remove_by_id.side_effect = RelationshipViolationError(
        detail="Невозможно удалить запись: на неё есть ссылки в других таблицах."
    )

    response = await client.delete("/employee/1")

    assert response.status_code == 409
    assert "ссылки в других таблицах" in response.json()["detail"]
