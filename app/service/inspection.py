import datetime
from typing import TypeVar

from sqlalchemy.exc import IntegrityError

from app.core.exception import (
    DuplicatedError,
    NotFoundError,
)
from app.core.model import Prescription
from app.core.model.inspection import Status
from app.repository.disease import DiseaseRepository
from app.repository.employee import EmployeeRepository
from app.repository.inspection import InspectionRepository
from app.repository.patient import PatientRepository
from app.repository.prescription import PrescriptionRepository

T = TypeVar("T")
R = TypeVar("R")

class InspectionService:
    def __init__(
            self,
            repository_inspection: InspectionRepository,
            repository_employee: EmployeeRepository,
            repository_patient: PatientRepository,
            repository_disease: DiseaseRepository,
            repository_prescription: PrescriptionRepository,

    ) -> None:
        self._repository_inspection = repository_inspection
        self._repository_employee = repository_employee
        self._repository_patient = repository_patient
        self._repository_disease = repository_disease
        self._repository_prescription = repository_prescription


    async def add(self, schema: T) -> R:
        try:
            employee_ = await self._repository_employee.exist(schema.doctor_id)
            if not employee_:
                raise NotFoundError(
                    detail="Employee не найден"
                )
            patient_ = await self._repository_patient.exist(schema.patient_id)
            if not patient_:
                raise NotFoundError(
                    detail="Пациент не найден"
                )

            obj = await self._repository_inspection.create(schema)
            await self._repository_inspection.session.commit()
            await self._repository_inspection.session.refresh(obj)
            return obj
        except IntegrityError:
            await self._repository_inspection.session.rollback()
            raise DuplicatedError(
                detail="Запись с такими уникальными атрибутами уже существует."
            )

    async def patch(self, id_: int, schema: T) -> T:
        try:
            obj_inspection = await self._repository_inspection.update(id_, schema)
            if obj_inspection is None:
                raise NotFoundError(
                    detail=f"Запись об обследовании с ID {id_} не найдена."
                )

            if schema.disease_ids:
                disease_exists = await self._repository_disease.all_exist(schema.disease_ids)
                if not disease_exists:
                    raise NotFoundError(
                        detail="Один или несколько диагнозов не существует в таблице"
                    )

            if schema.prescriptions_update:
                prescriptions_update_ids = [i.medicine_id for i in schema.prescriptions_update]
                prescription_exists = await self._repository_prescription.all_exist(prescriptions_update_ids)
                if not prescription_exists:
                    raise NotFoundError(
                        detail="Один или несколько лекарств в рецептах не существует в таблице update"
                    )


            if schema.address is not None:
                obj_inspection.address = schema.address
            if schema.symptoms is not None:
                obj_inspection.symptoms = schema.symptoms
            if schema.instructions is not None:
                obj_inspection.instructions = schema.instructions
            # пересоздаем для inspections связи с болезнями
            if schema.disease_ids is not None:
                await self._repository_inspection.update_diseases(id_, schema.disease_ids)
            # удаляем нужные рецепты
            if schema.prescriptions_delete_ids is not None:
                await self._repository_prescription.delete_all_by_id(schema.prescriptions_delete_ids)

            if schema.prescriptions_update is not None:
                db_prescriptions = [
                    Prescription(
                        inspection_id=id_,
                        medicine_id=p.medicine_id,
                        intake_method=p.intake_method,
                    )
                    for p in schema.prescriptions_update
                ]
                await self._repository_prescription.update_all(db_prescriptions)

            if schema.prescriptions_create is not None:
                db_prescriptions = [
                    Prescription(
                        inspection_id=id_,
                        medicine_id=p.medicine_id,
                        intake_method=p.intake_method,
                    )
                    for p in schema.prescriptions_create
                ]
                await self._repository_prescription.create_all(db_prescriptions)

            await self._repository_inspection.session.commit()
            await self._repository_inspection.session.refresh(obj_inspection)
            return obj_inspection
        except IntegrityError:
            await self._repository_inspection.session.rollback()
            raise DuplicatedError(
                detail="Обновление не выполнено из-за нарушения уникальности"
            )
        except Exception as e:
            await self._repository_inspection.session.rollback()
            raise e

    async def inspection_per_day(self, status: str | None = Status.COMPLETED, start: datetime.date | None = None, end: datetime.date | None = None) -> T:
        try:
            data = await self._repository_inspection.get_inspection_count_by_day(status, start, end)
            
