from typing import Any
from unittest.mock import AsyncMock

import pytest
from httpx import AsyncClient

from app.core.dependencies import (
    auth_bearer,
    get_patient_service,
)
from app.core.exception import (
    DuplicatedError,
    NotFoundError,
    RelationshipViolationError,
)
from app.core.exceptions_handler import register_exception_handlers
from app.core.schema.patient import PatientUpdate

payload_get = {
    "id": 1,
    "name": "Иванов Иван Иванович",
    "sex": "m",
    "phone_number": "89041231123",
    "born_date": "2000-10-12",
    "home_address": "г. Москва, ул. Морозова, д. 22, кв. 20",
}

payload_add = {
    "name": "Новый Пациент",
    "sex": "f",
    "phone_number": "89991112233",
    "born_date": "1995-05-05",
    "home_address": "г. Москва, ул. Пушкина, д. 12",
}

patch_name_payload = {"name": "Петров Иван Иванович"}

payload_patch = {**payload_get, **patch_name_payload}

payload_pagination: dict[str, Any] = {
    "founds": [payload_get],
    "total_count": 15,
}

@pytest.fixture(scope="function", autouse=True)
def mock_patient_service(app):
    register_exception_handlers(app)
    service = AsyncMock()

    # Подменяем зависимость
    app.dependency_overrides[get_patient_service] = lambda: service
    app.dependency_overrides[auth_bearer] = lambda: True

    service.get_by_id.return_value = payload_get

    service.add.return_value = {"id": 2, **payload_add}

    service.patch.return_value = payload_patch

    service.get_list.return_value = payload_pagination

    service.remove_by_id.return_value = True

    yield service

    app.dependency_overrides.clear()


# get /patient/1 200
@pytest.mark.asyncio
async def test_get_patient(client: AsyncClient, mock_patient_service: AsyncMock) -> None:
    response = await client.get("/patient/1")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["name"] == "Иванов Иван Иванович"
    assert data["sex"] == "m"
    assert data["phone_number"] == "89041231123"
    assert data["born_date"] == "2000-10-12"
    assert data["home_address"] == "г. Москва, ул. Морозова, д. 22, кв. 20"

    # Проверяем, что эндпоинт передал в сервис правильный ID (целое число, а не строку)
    mock_patient_service.get_by_id.assert_called_once_with(1)

# get /patient/1 404
@pytest.mark.asyncio
async def test_get_patient_not_found(client: AsyncClient, mock_patient_service: AsyncMock) -> None:
    mock_patient_service.get_by_id.side_effect = NotFoundError(
        detail="Пациент не найден"
    )

    response = await client.get("/patient/1")

    assert response.status_code == 404
    assert response.json()["detail"] == "Пациент не найден"
    mock_patient_service.get_by_id.assert_called_once_with(1)

# get /patient/{str} 422
@pytest.mark.asyncio
async def test_get_patient_invalid_id_type(client: AsyncClient, mock_patient_service: AsyncMock) -> None:
    response = await client.get("/patient/not-a-number")

    assert response.status_code == 422
    # Сервис вообще не должен вызываться, так как валидация упала на уровне FastAPI
    mock_patient_service.get_by_id.assert_not_called()

# post /patient/ 201
@pytest.mark.asyncio
async def test_create_patient_success(
    client: AsyncClient, mock_patient_service: AsyncMock
) -> None:
    response = await client.post("/patient/", json=payload_add)

    assert response.status_code == 201
    assert response.json()["id"] == 2
    mock_patient_service.add.assert_called_once()

# post /patient/ 422
@pytest.mark.asyncio
async def test_create_patient_invalid_body(client: AsyncClient, mock_patient_service: AsyncMock) -> None:
    response = await client.post("/patient/", json={})

    assert response.status_code == 422
    assert "detail" in response.json()
    mock_patient_service.add.assert_not_called()

# post /patient/ 409 (Дубликат, например, по номеру телефона)
@pytest.mark.asyncio
async def test_create_patient_duplicate(
    client: AsyncClient, mock_patient_service: AsyncMock
) -> None:
    mock_patient_service.add.side_effect = DuplicatedError(
        detail="Запись с такими уникальными атрибутами уже существует."
    )

    response = await client.post("/patient/", json=payload_add)

    assert response.status_code == 409
    assert "уникальными атрибутами" in response.json()["detail"]

# patch /patient/1 200
@pytest.mark.asyncio
async def test_update_patient_success(
    client: AsyncClient, mock_patient_service: AsyncMock
) -> None:
    response = await client.patch("/patient/1", json=patch_name_payload)

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["name"] == "Петров Иван Иванович"

    mock_patient_service.patch.assert_called_once_with(
        1,
        PatientUpdate(name="Петров Иван Иванович", sex=None, phone_number=None, born_date=None, home_address=None)
    )

# patch /patient/1 404
@pytest.mark.asyncio
async def test_update_patient_not_found(
    client: AsyncClient, mock_patient_service: AsyncMock
) -> None:
    # Имитируем, что сервис выбросил NotFoundError
    mock_patient_service.patch.side_effect = NotFoundError(detail="Запись с ID 1 не найдена.")

    response = await client.patch("/patient/1", json=patch_name_payload)

    assert response.status_code == 404
    assert response.json()["detail"] == "Запись с ID 1 не найдена."

# get /patient/ 200
@pytest.mark.asyncio
async def test_get_patients_list_pagination(
    client: AsyncClient, mock_patient_service: AsyncMock
) -> None:
    response = await client.get(
        "/patient/", params={"page": 1, "page_size": 1, "ordering": "name"}
    )

    assert response.status_code == 200
    data = response.json()

    # Проверяем структуру PaginatedResponse
    assert "founds" in data
    assert len(data["founds"]) == len(payload_pagination["founds"])
    assert data["founds"][0]["name"] == payload_get.get('name')
    assert data["total_count"] == payload_pagination.get('total_count')

    mock_patient_service.get_list.assert_called_once_with(
        page=1, page_size=1, ordering="name"
    )

# delete /patient/1 204
@pytest.mark.asyncio
async def test_delete_patient_success(client: AsyncClient, mock_patient_service: AsyncMock) -> None:
    response = await client.delete("/patient/1")

    assert response.status_code == 204
    assert response.content == b""  # Тело ответа абсолютно пустое
    mock_patient_service.remove_by_id.assert_called_once_with(1)

# delete /patient/1 404
@pytest.mark.asyncio
async def test_delete_patient_not_found(
    client: AsyncClient, mock_patient_service: AsyncMock
) -> None:
    # Имитируем поведение сервиса при отсутствии записи
    mock_patient_service.remove_by_id.side_effect = NotFoundError(detail="Запись с таким id не найдена")

    response = await client.delete("/patient/1")

    assert response.status_code == 404
    assert response.json()["detail"] == "Запись с таким id не найдена"

# delete /patient/1 409 (Есть привязанные данные в других таблицах)
@pytest.mark.asyncio
async def test_delete_patient_relationship_violation(
    client: AsyncClient, mock_patient_service: AsyncMock
) -> None:
    mock_patient_service.remove_by_id.side_effect = RelationshipViolationError(
        detail="Невозможно удалить запись: на неё есть ссылки в других таблицах."
    )

    response = await client.delete("/patient/1")

    assert response.status_code == 409
    assert "ссылки в других таблицах" in response.json()["detail"]
