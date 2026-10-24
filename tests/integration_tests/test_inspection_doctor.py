import datetime
from copy import copy
from typing import Any

import pytest

from app.core.dependencies import get_current_user_id, get_current_user_role
from app.core.model import (
    Disease,
    Employee,
    Inspection,
    Medicine,
    Patient,
    Prescription,
)
from app.util.hashing import get_password_hash

inspection_add: dict[str, Any] = {
    "inspection_at": None,
    "address": "Адрес больницы",
    "symptoms": "Симптомы",
    "instructions": "Инструкции",
    "status": None,
}

prescriptions_add = {
    # "medicine_id": int
    "intake_method": "Запить водой",
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
async def test_create_item(admin_client, app, session):
    add_data = copy(inspection_add)
    add_data_prescription = copy(prescriptions_add)

    response_patient = await admin_client.post("/patient/", json=patient_add)
    assert response_patient.status_code == 201
    patient_id = response_patient.json()["id"]
    add_data["patient_id"] = patient_id

    response_doctor = await admin_client.post("/employee/", json=doctor_add)
    assert response_doctor.status_code == 201
    doctor_id = response_doctor.json()["id"]
    add_data["doctor_id"] = doctor_id

    response_disease = await admin_client.post("/disease/", json=disease_add)
    assert response_disease.status_code == 201
    disease_id = response_disease.json()["id"]
    add_data["disease_ids"] = [
        disease_id,
    ]

    response_medicine = await admin_client.post("/medicine/", json=medicine_add)
    assert response_medicine.status_code == 201
    medicine_id = response_medicine.json()["id"]

    add_data_prescription["medicine_id"] = medicine_id
    add_data["prescriptions_create"] = [
        add_data_prescription,
    ]

    app.dependency_overrides[get_current_user_role] = lambda: "doctor"
    app.dependency_overrides[get_current_user_id] = lambda: doctor_id

    response = await admin_client.post("/inspection/doctor/", json=add_data)

    assert response.status_code == 201
    data = response.json()
    print(data)
    assert data["doctor_id"] == doctor_id
    assert data["patient_id"] == patient_id
    assert data["inspection_at"] == inspection_add["inspection_at"]
    assert data["address"] == inspection_add["address"]


@pytest.mark.asyncio
async def test_read_item(session, client, as_doctor):
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

    test_disease = Disease(**disease_add)
    session.add(test_disease)
    await session.flush()

    test_medicine = Medicine(**medicine_add)
    session.add(test_medicine)
    await session.flush()
    medicine_id = test_medicine.id

    test_inspection = Inspection(
        **inspection_add,
        doctor_id=doctor_id,
        patient_id=patient_id,
        diseases=[
            test_disease,
        ],
    )
    session.add(test_inspection)
    await session.flush()
    inspection_id = test_inspection.id

    test_prescription = Prescription(
        **prescriptions_add, medicine_id=medicine_id, inspection_id=inspection_id
    )
    session.add(test_prescription)
    await session.flush()

    await session.commit()

    response = await client.get(f"/inspection/doctor/{inspection_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["doctor_id"] == doctor_id
    assert data["patient_id"] == patient_id
    assert data["address"] == inspection_add["address"]
    assert data["diseases"] == [
        disease_add,
    ]
    assert "prescriptions" in data


@pytest.mark.asyncio
async def test_item_not_found(client, as_doctor):
    response = await client.get("/inspection/doctor/999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_item_wrong_param(client, as_doctor):
    response = await client.get("/inspection/doctor/a")
    assert response.status_code == 422
    assert "detail" in response.json()
