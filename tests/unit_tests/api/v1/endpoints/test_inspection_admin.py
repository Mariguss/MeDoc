from typing import Any
from unittest.mock import AsyncMock

import pytest
from httpx import AsyncClient

from app.core.dependencies import (
    auth_bearer,
    get_inspection_service,
)
from app.core.exception import (
    DuplicatedError,
    NotFoundError,
)
from app.core.exceptions_handler import register_exception_handlers
from app.core.schema.inspection import (
    InspectionUpdateAdmin,
)

fake_doctor = {
    "login": "admin_test",
    "name": "Иванов Иван Иванович",
    "speciality": "Терапевт",
}

fake_patient = {
    "name": "Петров Петр Петрович",
    "sex": "m",
    "phone_number": "79991112233",
    "born_date": "1990-01-01",
    "home_address": "Москва",
}

payload_get = {
    "id": 1,
    "doctor_id": 1,
    "patient_id": 1,
    "inspection_at": None,
    "created_at": "2026-10-23T18:00:00",
    "updated_at": "2026-10-23T18:00:00",
    "address": "адрес больницы",
    "doctor": fake_doctor,
    "patient": fake_patient,
}

payload_add = {
    "doctor_id": 2,
    "patient_id": 2,
    "inspection_at": None,
    "created_at": "2026-10-23T18:00:00",
    "updated_at": "2026-10-23T18:00:00",
    "address": "адрес больницы",
    "doctor": fake_doctor,
    "patient": fake_patient,
}

patch_inspection_at_payload = {"inspection_at": "2026-10-23T18:00:00"}

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
    app.dependency_overrides[auth_bearer] = lambda: {"role": "admin"}

    service.get_by_id.return_value = payload_get
    service.add_by_admin.return_value = {"id": 2, **payload_add}
    service.patch_by_admin.return_value = payload_patch
    service.get_list.return_value = payload_pagination

    yield service

    app.dependency_overrides.clear()


# get /inspection/admin/1 200
@pytest.mark.asyncio
async def test_get_inspection(
    client: AsyncClient, mock_inspection_service: AsyncMock
) -> None:
    response = await client.get("/inspection/admin/1")

    assert response.status_code == 200
    data = response.json()
    assert data["doctor_id"] == 1
    assert data["patient_id"] == 1
    assert data["inspection_at"] is None
    assert data["created_at"] == "2026-10-23T18:00:00"
    assert data["updated_at"] == "2026-10-23T18:00:00"
    assert data["address"] == "адрес больницы"
    assert data.get("doctor") is None

    mock_inspection_service.get_by_id.assert_called_once_with(1)


# get /inspection/admin/1 404
@pytest.mark.asyncio
async def test_get_inspection_not_found(
    client: AsyncClient, mock_inspection_service: AsyncMock
) -> None:
    mock_inspection_service.get_by_id.side_effect = NotFoundError(
        detail="Инспекция не найдена"
    )

    response = await client.get("/inspection/admin/1")

    assert response.status_code == 404
    assert response.json()["detail"] == "Инспекция не найдена"
    mock_inspection_service.get_by_id.assert_called_once_with(1)


# get /inspection/admin/{str} 422
@pytest.mark.asyncio
async def test_get_inspection_invalid_id_type(
    client: AsyncClient, mock_inspection_service: AsyncMock
) -> None:
    response = await client.get("/inspection/admin/not-a-number")

    assert response.status_code == 422
    mock_inspection_service.get_by_id.assert_not_called()


# post /inspection/admin 201
@pytest.mark.asyncio
async def test_create_inspection_success(
    client: AsyncClient, mock_inspection_service: AsyncMock
) -> None:
    response = await client.post("/inspection/admin/", json=payload_add)

    assert response.status_code == 201
    data = response.json()
    assert data["doctor_id"] == 2
    assert "created_at" in data
    assert "updated_at" in data
    mock_inspection_service.add_by_admin.assert_called_once()


# post /inspection/admin 422
@pytest.mark.asyncio
async def test_create_inspection_invalid_body(
    client: AsyncClient, mock_inspection_service: AsyncMock
) -> None:
    response = await client.post("/inspection/admin/", json={})

    assert response.status_code == 422
    assert "detail" in response.json()
    mock_inspection_service.add_by_admin.assert_not_called()


# post /inspection/admin 409
@pytest.mark.asyncio
async def test_create_inspection_duplicate(
    client: AsyncClient, mock_inspection_service: AsyncMock
) -> None:
    mock_inspection_service.add_by_admin.side_effect = DuplicatedError(
        detail="Запись с такими уникальными атрибутами уже существует."
    )

    response = await client.post("/inspection/admin/", json=payload_add)

    assert response.status_code == 409
    assert "уникальными атрибутами" in response.json()["detail"]


# patch /inspection/admin/1 200
@pytest.mark.asyncio
async def test_update_inspection_success(
    client: AsyncClient, mock_inspection_service: AsyncMock
) -> None:
    response = await client.patch(
        "/inspection/admin/1", json=patch_inspection_at_payload
    )

    assert response.status_code == 200
    data = response.json()
    assert data["doctor_id"] == 1
    assert data["inspection_at"] == payload_patch["inspection_at"]

    mock_inspection_service.patch_by_admin.assert_called_once_with(
        1,
        InspectionUpdateAdmin(
            doctor_id=None,
            patient_id=None,
            # Используем игнорирование типа конкретно для этой строки в тесте
            inspection_at=payload_patch["inspection_at"],  # type: ignore[arg-type]
            address=None,
        ),
    )


# patch /inspection/admin/1 404
@pytest.mark.asyncio
async def test_update_inspection_not_found(
    client: AsyncClient, mock_inspection_service: AsyncMock
) -> None:
    mock_inspection_service.patch_by_admin.side_effect = NotFoundError(
        detail="Запись с ID 1 не найдена."
    )

    response = await client.patch(
        "/inspection/admin/1", json=patch_inspection_at_payload
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Запись с ID 1 не найдена."


# patch /inspection/ 200
@pytest.mark.asyncio
async def test_get_inspections_list_admin_success(
    client: AsyncClient, mock_inspection_service: AsyncMock
) -> None:
    response = await client.patch(
        "/inspection/admin/", json={"address": "адрес больницы"}
    )

    assert response.status_code == 200
    data = response.json()

    assert "founds" in data
    assert "total_count" in data
    assert data["total_count"] == 15
    assert data["founds"][0]["address"] == "адрес больницы"

    mock_inspection_service.get_list.assert_called_once_with(address="адрес больницы")
