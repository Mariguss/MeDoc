import pytest

from app.core.model import Employee
from app.util.hashing import get_password_hash

employee_add = {
    "login": "test_login",
    "password": "Aa123456!",
    "name": "Яковлев Арсений Александрович",
    "role": "doctor",
    "speciality": "ЛОР",
}


@pytest.mark.asyncio
async def test_create_item(client, session, as_admin):
    response = await client.post("/employee/", json=employee_add)

    assert response.status_code == 201
    data = response.json()
    assert data["login"] == employee_add["login"]
    assert data["name"] == employee_add["name"]
    assert data["role"] == employee_add["role"]
    assert data["speciality"] == employee_add["speciality"]

    assert "created_at" in data
    assert "updated_at" in data


@pytest.mark.asyncio
async def test_read_item(session, client, as_admin):
    # Передаем db_session прямо в тест для изолированной вставки данных
    password_hash = get_password_hash(str(employee_add.pop("password")))
    test_item = Employee(**employee_add, password_hash=password_hash)
    session.add(test_item)
    await session.flush()
    item_id = test_item.id
    await session.commit()

    response = await client.get(f"/employee/{item_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == item_id
    assert data["name"] == employee_add["name"]
    assert data["role"] == employee_add["role"]
    assert data["speciality"] == employee_add["speciality"]
    assert "created_at" in data
    assert "updated_at" in data


@pytest.mark.asyncio
async def test_item_not_found(client, as_admin):
    response = await client.get("/employee/999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_item_wrong_param(client, as_admin):
    response = await client.get("/employee/a")
    assert response.status_code == 422
    assert "detail" in response.json()
