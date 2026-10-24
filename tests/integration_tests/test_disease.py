import pytest

from app.core.model import Disease

payload_add = {
    "name": "Простуда",
}

@pytest.mark.asyncio
async def test_create_item(client, as_admin):
    response = await client.post("/disease/", json=payload_add)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == payload_add["name"]
    assert "id" in data


@pytest.mark.asyncio
async def test_read_item(session, client, as_admin):
    # Передаем db_session прямо в тест для изолированной вставки данных
    test_item = Disease(name="ОРВИ")
    session.add(test_item)
    await session.flush()
    item_id = test_item.id
    await session.commit()

    response = await client.get(f"/disease/{item_id}")
    assert response.status_code == 200
    assert response.json()["id"] == item_id
    assert response.json()["name"] == "ОРВИ"


@pytest.mark.asyncio
async def test_item_not_found(client, as_admin):
    response = await client.get("/disease/999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_item_wrong_param(client, as_admin):
    response = await client.get("/disease/a")
    assert response.status_code == 422
    assert "detail" in response.json()
