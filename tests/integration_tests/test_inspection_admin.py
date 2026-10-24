import datetime
from copy import copy

import pytest
from util.hashing import get_password_hash

from app.core.model import Employee, Inspection, Patient

inspection_add = {
    "inspection_at": None,
    "address": "Адрес больницы",
}

patient_add = {
    "name": "Новый Пациент",
    "sex": "f",
    "phone_number": "89991112233",
    "born_date": "1995-05-05",
    "home_address": "г. Москва, ул. Пушкина, д. 12",
}

doctor_add = {
    "login": "test_login",
    "password": "Aa123456!",
    "name": "Яковлев Арсений Александрович",
    "role": "doctor",
    "speciality": "ЛОР",
}

disease_add = {
    "name": "Простуда",
}

medicine_add = {
    "name": "Ношпа",
    "properties": "Описание",
    "side_effects": "Эффекты",
}

@pytest.mark.asyncio
async def test_create_item(client, session, as_admin):
    add_data = copy(inspection_add)
    
    response_patient = await client.post("/patient/", json=patient_add)
    assert response_patient.status_code == 201
    patient_id = response_patient.json()["id"]
    add_data["patient_id"] = patient_id
    
    response_doctor = await client.post("/employee/", json=doctor_add)
    assert response_doctor.status_code == 201
    doctor_id = response_doctor.json()["id"]
    add_data["doctor_id"] = doctor_id

    response = await client.post("/inspection/admin/", json=add_data)

    assert response.status_code == 201
    data = response.json()
    assert data["doctor_id"] == doctor_id
    assert data["patient_id"] == patient_id
    assert data["inspection_at"] == inspection_add["inspection_at"]
    assert data["address"] == inspection_add["address"]



@pytest.mark.asyncio
async def test_read_item(session, client, as_admin):
    # Передаем db_session прямо в тест для изолированной вставки данных
    add_data_doctor = copy(doctor_add)
    password_hash = get_password_hash(str(add_data_doctor.pop("password")))
    test_doctor = Employee(**add_data_doctor, password_hash=password_hash)
    session.add(test_doctor)
    await session.flush()
    doctor_id = test_doctor.id

    add_data_patient = copy(patient_add)
    born_date = datetime.date.fromisoformat(add_data_patient.pop("born_date"))
    test_patient = Patient(**add_data_patient, born_date=born_date)
    session.add(test_patient)
    await session.flush()
    patient_id = test_patient.id

    test_inspection = Inspection(**inspection_add, doctor_id=doctor_id, patient_id=patient_id)
    session.add(test_inspection)
    await session.flush()
    inspection_id = test_inspection.id
    await session.commit()

    response = await client.get(f"/inspection/admin/{inspection_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == inspection_id
    assert data["doctor_id"] == doctor_id
    assert data["patient_id"] == patient_id
    assert data["address"] == inspection_add["address"]


@pytest.mark.asyncio
async def test_item_not_found(client, as_admin):
    response = await client.get("/inspection/admin/999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_item_wrong_param(client, as_admin):
    response = await client.get("/inspection/admin/a")
    assert response.status_code == 422
    assert "detail" in response.json()
