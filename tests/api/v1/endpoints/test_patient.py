from unittest.mock import AsyncMock

import pytest
from httpx import AsyncClient

from app.core.dependencies import (
    auth_bearer,
    get_patient_service,
)
from app.core.schema.patient import PatientUpdate  # Импортируем вашу схему


@pytest.fixture(scope="function", autouse=True)
def mock_patient_service(app):
    service = AsyncMock()
    service.login.return_value = (
        "fake_access_token",
        "fake_refresh_token",
        "2026-10-12T17:06:00",
    )

    # Подменяем зависимость
    app.dependency_overrides[get_patient_service] = lambda: service
    app.dependency_overrides[auth_bearer] = lambda: True
    service.get_by_id.return_value = {
        "id": 1,
        "name": "Иван Иванов",
        "sex": "f",
        "phone_number": "89041231123",
        "born_date": "2020-10-12",
        "home_address": "домашний адрес",
    }

    yield service

    app.dependency_overrides = {}


@pytest.mark.asyncio
async def test_get_patient(client: AsyncClient, mock_patient_service: AsyncMock) -> None:
    response = await client.get("/patient/1")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["name"] == "Иван Иванов"
    assert data["sex"] == "f"

    # Проверяем, что эндпоинт передал в сервис правильный ID (целое число, а не строку)
    mock_patient_service.get_by_id.assert_called_once_with(1)

@pytest.mark.asyncio
async def test_get_patient_not_found(client: AsyncClient, mock_patient_service: AsyncMock) -> None:
    # Переопределяем дефолтное значение фикстуры только для этого теста
    mock_patient_service.get_by_id.return_value = None

    response = await client.get("/patient/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Пациент не найден"
    mock_patient_service.get_by_id.assert_called_once_with(999)

@pytest.mark.asyncio
async def test_get_patient_invalid_id_type(client: AsyncClient, mock_patient_service: AsyncMock) -> None:
    response = await client.get("/patient/not-a-number")

    assert response.status_code == 422
    # Сервис вообще не должен вызываться, так как валидация упала на уровне FastAPI
    mock_patient_service.get_by_id.assert_not_called()

@pytest.mark.asyncio
async def test_create_patient_invalid_body(client: AsyncClient, mock_patient_service: AsyncMock) -> None:
    # Отправляем пустой JSON, который не пройдет валидацию схемы PatientCreate
    response = await client.post("/patient/", json={})

    assert response.status_code == 422
    assert "detail" in response.json()
    mock_patient_service.add.assert_not_called()

@pytest.mark.asyncio
async def test_delete_patient_success(client: AsyncClient, mock_patient_service: AsyncMock) -> None:
    mock_patient_service.remove_by_id.return_value = True

    response = await client.delete("/patient/1")

    assert response.status_code == 204
    assert response.content == b""  # Тело ответа абсолютно пустое
    mock_patient_service.remove_by_id.assert_called_once_with(1)

@pytest.mark.asyncio
async def test_create_patient_success(
    client: AsyncClient, mock_patient_service: AsyncMock
) -> None:
    # Данные, которые мы отправляем
    valid_payload = {
        "name": "Новый Пациент",
        "sex": "m",
        "phone_number": "89991112233",
        "born_date": "1995-05-05",
        "home_address": "ул. Пушкина",
    }

    # Что должен вернуть сервис (добавляется ID)
    mock_patient_service.add.return_value = {"id": 2, **valid_payload}

    response = await client.post("/patient/", json=valid_payload)

    assert response.status_code == 201
    assert response.json()["id"] == 2
    mock_patient_service.add.assert_called_once()

@pytest.mark.asyncio
async def test_update_patient_success(
    client: AsyncClient, mock_patient_service: AsyncMock
) -> None:
    # Отправляем только те поля, которые хотим изменить
    patch_payload = {"name": "Иван Петров"}

    mock_patient_service.patch.return_value = {
        "id": 1,
        "name": "Иван Петров",
        "sex": "f",
        "phone_number": "89041231123",
        "born_date": "2020-10-12",
        "home_address": "домашний адрес",
    }

    response = await client.patch("/patient/1", json=patch_payload)

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["name"] == "Иван Петров"

    # ИСПРАВЛЕНО: проверяем вызов с объектом PatientUpdate, который построил FastAPI
    mock_patient_service.patch.assert_called_once_with(
        1,
        PatientUpdate(name="Иван Петров", sex=None, phone_number=None, born_date=None, home_address=None)
    )

@pytest.mark.asyncio
async def test_get_patients_list_pagination(
    client: AsyncClient, mock_patient_service: AsyncMock
) -> None:
    # Данные одного пациента, которые соответствуют схеме PatientResponse
    patient_data = {
        "id": 2,
        "name": "Анна Сидорова",
        "sex": "f",
        "phone_number": "89051112233",
        "born_date": "1990-01-01",
        "home_address": "адрес",
    }

    # Сервис возвращает структуру, строго соответствующую PaginatedResponse
    mock_patient_service.get_list.return_value = {
        "founds": [patient_data],  # Список объектов T (PatientResponse)
        "total_count": 15,
    }

    # Делаем запрос со своими параметрами пагинации и сортировки
    response = await client.get(
        "/patient/", params={"page": 2, "page_size": 1, "ordering": "name"}
    )

    assert response.status_code == 200
    data = response.json()

    # Проверяем структуру PaginatedResponse согласно вашему классу
    assert "founds" in data
    assert len(data["founds"]) == 1
    assert data["founds"][0]["name"] == "Анна Сидорова"
    assert data["total_count"] == 15

    # Проверяем, что параметры корректно пробросились из роутера в метод сервиса
    mock_patient_service.get_list.assert_called_once_with(
        page=2, page_size=1, ordering="name"
    )
