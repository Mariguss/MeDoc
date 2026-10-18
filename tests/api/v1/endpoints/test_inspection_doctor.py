from typing import Any
from unittest.mock import AsyncMock

import pytest
from httpx import AsyncClient

from app.core.dependencies import (
    auth_bearer,
    get_current_user_id,
    get_inspection_service,
)
from app.core.exception import (
    DuplicatedError,
    NotFoundError,
)
from app.core.exceptions_handler import register_exception_handlers
from app.core.schema.inspection import (
    InspectionUpdateDoctor,
)

payload_get = {
    "id": 1,
    "doctor_id": 1,
    "patient_id": 1,
    "inspection_at": None,
    "created_at": "2026-07-09T00:00:00",
    "updated_at": "2026-07-09T00:00:00",
    "address": "адрес больницы",
    "symptoms": None,
    "instructions": None,
}

payload_add_request = {
    "patient_id": 2,
    "inspection_at": None,
    "address": "адрес больницы",
    "symptoms": None,
    "instructions": None,
}

payload_add_response = {
    "id": 2,
    "doctor_id": 1,
    **payload_add_request,
    "created_at": "2026-07-09T00:00:00",
    "updated_at": "2026-07-09T00:00:00",
}

patch_inspection_at_payload = {"inspection_at": "2026-07-09T00:00:00"}

payload_patch = {**payload_get, **patch_inspection_at_payload}

payload_pagination: dict[str, Any] = {
    "founds": [payload_get],
    "total_count": 15,
}

@pytest.fixture(scope="function", autouse=True)
def mock_inspection_service(app):
    register_exception_handlers(app)
    service = AsyncMock()

    app.dependency_overrides[get_inspection_service] = lambda: service
    app.dependency_overrides[auth_bearer] = lambda: {"role": "doctor"}
    app.dependency_overrides[get_current_user_id] = lambda: 1

    service.get_by_id.return_value = payload_get

    service.add_by_doctor.return_value = payload_add_response

    service.patch_by_doctor.return_value = payload_patch

    service.get_list.return_value = payload_pagination

    yield service

    app.dependency_overrides.clear()


# post /inspection/doctor 201
@pytest.mark.asyncio
async def test_create_inspection_success(
    client: AsyncClient, mock_inspection_service: AsyncMock
) -> None:
    response = await client.post("/inspection/doctor/", json=payload_add_request)

    assert response.status_code == 201
    assert response.json()["id"] == 2
    assert response.json()["doctor_id"] == 1
    mock_inspection_service.add_by_doctor.assert_called_once()

# post /inspection/doctor 422
@pytest.mark.asyncio
async def test_create_inspection_invalid_body(client: AsyncClient, mock_inspection_service: AsyncMock) -> None:
    response = await client.post("/inspection/doctor/", json={})

    assert response.status_code == 422
    assert "detail" in response.json()
    mock_inspection_service.add_by_doctor.assert_not_called()

# post /inspection/doctor 409 (Дубликат, например, по номеру телефона)
@pytest.mark.asyncio
async def test_create_inspection_duplicate(
    client: AsyncClient, mock_inspection_service: AsyncMock
) -> None:
    mock_inspection_service.add_by_doctor.side_effect = DuplicatedError(
        detail="Запись с такими уникальными атрибутами уже существует."
    )

    response = await client.post("/inspection/doctor/", json=payload_add_request)

    assert response.status_code == 409
    assert "уникальными атрибутами" in response.json()["detail"]

# patch /inspection/doctor/1 200
@pytest.mark.asyncio
async def test_update_inspection_success(
    client: AsyncClient, mock_inspection_service: AsyncMock
) -> None:
    response = await client.patch("/inspection/doctor/1", json=patch_inspection_at_payload)

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["inspection_at"] == payload_patch.get('inspection_at')

    mock_inspection_service.patch_by_doctor.assert_called_once_with(
        1,
        InspectionUpdateDoctor(
            patient_id=None,
            address=None,
            symptoms=None,
            instructions=None,
            status=None,
            disease_ids=None,
            prescriptions_update=None,
            prescriptions_delete_ids=None,
            prescriptions_create=None,
            inspection_at=payload_patch.get("inspection_at"),
        ),
    )

# patch /inspection/doctor/1 404
@pytest.mark.asyncio
async def test_update_inspection_not_found(
    client: AsyncClient, mock_inspection_service: AsyncMock
) -> None:
    # Имитируем, что сервис выбросил NotFoundError
    mock_inspection_service.patch_by_doctor.side_effect = NotFoundError(detail="Запись с ID 1 не найдена.")

    response = await client.patch("/inspection/doctor/1", json=patch_inspection_at_payload)

    assert response.status_code == 404
    assert response.json()["detail"] == "Запись с ID 1 не найдена."
