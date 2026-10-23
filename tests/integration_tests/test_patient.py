import datetime

import pytest

from app.core.model import Patient

patient_add = {
    "name": "Потапов Олег Анатольевич",
    "sex": "m",
    "phone_number": "79002341551",
    "born_date": "1995-05-15",
    "home_address": "Домашний адрес",
}


@pytest.mark.asyncio
async def test_create_item(client, session, as_admin):
    response = await client.post("/patient/", json=patient_add)

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == patient_add["name"]
    assert data["sex"] == patient_add["sex"]
    assert data["phone_number"] == patient_add["phone_number"]
    assert data["home_address"] == patient_add["home_address"]
    assert "born_date" in data
    assert "created_at" in data


@pytest.mark.asyncio
async def test_read_item(session, client, as_admin):
    # Передаем db_session прямо в тест для изолированной вставки данных
    born_date = datetime.date.fromisoformat(patient_add.pop("born_date"))
    test_item = Patient(**patient_add, born_date=born_date)
    session.add(test_item)
    await session.flush()
    item_id = test_item.id
    await session.commit()

    response = await client.get(f"/patient/{item_id}")
    assert response.status_code == 200
    assert response.json()["id"] == item_id
    assert response.json()["name"] == patient_add["name"]


@pytest.mark.asyncio
async def test_item_not_found(client, as_admin):
    response = await client.get("/patient/999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_item_wrong_param(client, as_admin):
    response = await client.get("/patient/a")
    assert response.status_code == 422
    assert "detail" in response.json()
