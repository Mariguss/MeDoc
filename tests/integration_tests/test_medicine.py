import pytest

from app.core.model import Medicine

payload_add = {
    "name": "Ношпа",
    "properties": "Описание",
    "side_effects": "Эффекты",
}


@pytest.mark.asyncio
async def test_create_item(client, as_admin):
    response = await client.post("/medicine/", json=payload_add)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == payload_add["name"]
    assert data["properties"] == payload_add["properties"]
    assert data["side_effects"] == payload_add["side_effects"]
    assert "id" in data


@pytest.mark.asyncio
async def test_read_item(session, client, as_admin):
    # Передаем db_session прямо в тест для изолированной вставки данных
    test_item = Medicine(**payload_add)
    session.add(test_item)
    await session.flush()
    item_id = test_item.id
    await session.commit()

    response = await client.get(f"/medicine/{item_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == item_id
    assert data["name"] == payload_add["name"]
    assert data["properties"] == payload_add["properties"]
    assert data["side_effects"] == payload_add["side_effects"]


@pytest.mark.asyncio
async def test_item_not_found(client, as_admin):
    response = await client.get("/medicine/999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_item_wrong_param(client, as_admin):
    response = await client.get("/medicine/a")
    assert response.status_code == 422
    assert "detail" in response.json()
