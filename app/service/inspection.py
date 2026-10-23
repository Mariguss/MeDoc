from typing import Any, TypeVar, cast

from loguru import logger
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.core.exception import (
    DuplicatedError,
    NotFoundError,
)
from app.core.model import Inspection, Prescription
from app.core.schema.inspection import (
    InspectionCreateAdmin,
    InspectionCreateDoctorInternal,
    InspectionPerDateRequest,
    InspectionResponseAdmin,
    InspectionResponseDoctor,
    InspectionUpdateAdmin,
    InspectionUpdateDoctor,
)
from app.repository.disease import DiseaseRepository
from app.repository.employee import EmployeeRepository
from app.repository.inspection import InspectionRepository
from app.repository.medicine import MedicineRepository
from app.repository.patient import PatientRepository
from app.repository.prescription import PrescriptionRepository
from app.service.base import BaseService

T = TypeVar("T")
R = TypeVar("R")


class InspectionService(BaseService):
    def __init__(
        self,
        repository_inspection: InspectionRepository,
        repository_employee: EmployeeRepository,
        repository_patient: PatientRepository,
        repository_disease: DiseaseRepository,
        repository_prescription: PrescriptionRepository,
        repository_medicine: MedicineRepository,
    ) -> None:
        super().__init__(repository_inspection, Inspection)
        self._repository_inspection = repository_inspection
        self._repository_employee = repository_employee
        self._repository_patient = repository_patient
        self._repository_disease = repository_disease
        self._repository_prescription = repository_prescription
        self._repository_medicine = repository_medicine

        self._model_class = Inspection

    async def add_by_admin(self, schema: InspectionCreateAdmin):
        try:
            employee_ = await self._repository_employee.exist(schema.doctor_id)
            if not employee_:
                raise NotFoundError(detail="Доктор не найден")
            patient_ = await self._repository_patient.exist(schema.patient_id)
            if not patient_:
                raise NotFoundError(detail="Пациент не найден")
            db_obj = self._model_class(**schema.model_dump())
            obj = await self._repository_inspection.create(cast(Inspection, db_obj))
            await self._repository_inspection.session.commit()
            await self._repository_inspection.session.refresh(obj)
            return obj
        except NotFoundError:
            await self._repository_inspection.session.rollback()
            raise
        except IntegrityError:
            await self._repository_inspection.session.rollback()
            logger.exception("Ошибка в функции add_by_admin (IntegrityError)")
            raise DuplicatedError(
                detail="Запись с такими уникальными атрибутами уже существует."
            )
        except SQLAlchemyError:
            logger.exception("Ошибка в функции add_by_admin (SQLAlchemyError)")
            await self._repository_inspection.session.rollback()
            raise

    async def add_by_doctor(
        self, schema: InspectionCreateDoctorInternal
    ) -> InspectionResponseDoctor:
        try:
            employee_ = await self._repository_employee.exist(schema.doctor_id)
            if not employee_:
                raise NotFoundError(detail="Доктор не найден")
            patient_ = await self._repository_patient.exist(schema.patient_id)
            if not patient_:
                raise NotFoundError(detail="Пациент не найден")

            if schema.disease_ids:
                disease_exists = await self._repository_disease.all_exist(
                    schema.disease_ids
                )
                if not disease_exists:
                    raise NotFoundError(
                        detail="Один или несколько диагнозов не существует в таблице"
                    )

            inspection_data = schema.model_dump(
                exclude={"disease_ids", "prescriptions_create"}
            )
            db_obj = self._model_class(**inspection_data)

            inspection_obj = await self._repository_inspection.create(
                cast(Inspection, db_obj)
            )
            await self._repository_inspection.session.flush()

            # создаем для inspections связи с болезнями
            if schema.disease_ids is not None:
                await self._repository_inspection.update_diseases(
                    inspection_obj.id, schema.disease_ids
                )

            if schema.prescriptions_create is not None:
                db_prescriptions = [
                    Prescription(
                        inspection_id=inspection_obj.id,
                        medicine_id=p.medicine_id,
                        intake_method=p.intake_method,
                    )
                    for p in schema.prescriptions_create
                ]

                await self._repository_prescription.create_all(db_prescriptions)

            await self._repository_inspection.session.commit()
            await self._repository_inspection.session.refresh(inspection_obj)
            return cast(InspectionResponseDoctor, cast(Any, inspection_obj))
        except NotFoundError:
            await self._repository_inspection.session.rollback()
            raise
        except IntegrityError:
            logger.exception("Ошибка в функции add_by_doctor (IntegrityError)")
            await self._repository_inspection.session.rollback()
            raise DuplicatedError(
                detail="Запись с такими уникальными атрибутами уже существует."
            )
        except SQLAlchemyError:
            logger.exception("Ошибка в функции add_by_doctor (SQLAlchemyError)")
            await self._repository_inspection.session.rollback()
            raise

    async def patch_by_admin(
        self, id_: int, schema: InspectionUpdateAdmin
    ) -> InspectionResponseAdmin:
        try:
            if schema.doctor_id is not None:
                employee_ = await self._repository_employee.exist(schema.doctor_id)
                if not employee_:
                    raise NotFoundError(detail="Доктор не найден")
            if schema.patient_id is not None:
                patient_ = await self._repository_patient.exist(schema.patient_id)
                if not patient_:
                    raise NotFoundError(detail="Пациент не найден")
            obj_inspection = await self._repository_inspection.read_by_id(id_)
            if obj_inspection is None:
                raise NotFoundError(detail=f"Запись с ID {id_} не найдена.")

            update_data = schema.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(obj_inspection, key, value)

            await self._repository_inspection.update()

            await self._repository_inspection.session.commit()
            await self._repository_inspection.session.refresh(obj_inspection)
            return cast(InspectionResponseAdmin, cast(Any, obj_inspection))
        except NotFoundError:
            await self._repository_inspection.session.rollback()
            raise
        except IntegrityError:
            await self._repository_inspection.session.rollback()
            logger.exception("Ошибка в функции patch_by_admin (IntegrityError)")
            raise DuplicatedError(
                detail="Обновление не выполнено из-за нарушения уникальности"
            )
        except SQLAlchemyError:
            await self._repository_inspection.session.rollback()
            logger.exception("Ошибка в функции patch_by_admin (SQLAlchemyError)")
            raise

    async def patch_by_doctor(
        self, id_: int, schema: InspectionUpdateDoctor
    ) -> InspectionResponseDoctor:
        try:
            if schema.patient_id is not None:
                patient_ = await self._repository_patient.exist(schema.patient_id)
                if not patient_:
                    raise NotFoundError(detail="Пациент не найден")

            obj_inspection = await self._repository_inspection.read_by_id(id_)
            if obj_inspection is None:
                raise NotFoundError(detail=f"Запись с ID {id_} не найдена.")

            if schema.disease_ids:
                for disease_id_ in schema.disease_ids:
                    if not await self._repository_disease.exist(disease_id_):
                        raise NotFoundError(
                            detail="Один или несколько диагнозов не существует в таблице"
                        )

            if schema.address is not None:
                obj_inspection.address = schema.address
            if schema.symptoms is not None:
                obj_inspection.symptoms = schema.symptoms
            if schema.instructions is not None:
                obj_inspection.instructions = schema.instructions

            # пересоздаем для inspections связи с болезнями
            if schema.disease_ids is not None:
                await self._repository_inspection.update_diseases(
                    id_, schema.disease_ids
                )
            # удаляем рецепты
            if schema.prescriptions_delete_ids is not None:
                for prescriptions_delete_id_ in schema.prescriptions_delete_ids:
                    await self._repository_prescription.delete_by_id(
                        prescriptions_delete_id_
                    )
            # проверить существуют ли лекарства
            if schema.prescriptions_update is not None:
                for p_schema in schema.prescriptions_update:
                    db_prescription = await self._repository_prescription.read_by_id(
                        p_schema.id
                    )
                    if db_prescription is None:
                        raise NotFoundError(
                            detail=f"Рецепт с ID {p_schema.id} не найден."
                        )
                    prescriptions_update_data = p_schema.model_dump(
                        exclude={"id"}, exclude_unset=True
                    )
                    if prescriptions_update_data.get("medicine_id") is not None:
                        is_exist = await self._repository_medicine.exist(
                            prescriptions_update_data["medicine_id"]
                        )
                        if not is_exist:
                            raise NotFoundError(
                                detail=f"В рецепте с id {p_schema.id} указано несуществующее лекарство"
                            )
                    for key, value in prescriptions_update_data.items():
                        setattr(db_prescription, key, value)
                await self._repository_prescription.update()

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
            return cast(InspectionResponseDoctor, cast(Any, obj_inspection))
        except NotFoundError:
            await self._repository_inspection.session.rollback()
            raise
        except IntegrityError:
            await self._repository_inspection.session.rollback()
            logger.exception("Ошибка в функции patch_by_doctor (IntegrityError)")
            raise DuplicatedError(
                detail="Обновление не выполнено из-за нарушения уникальности"
            )
        except SQLAlchemyError:
            await self._repository_inspection.session.rollback()
            logger.exception("Ошибка в функции patch_by_doctor (SQLAlchemyError)")
            raise

    async def inspection_per_day(self, schema: InspectionPerDateRequest) -> list:
        try:
            data = await self._repository_inspection.get_inspection_count_by_day(
                schema.status, schema.start_date, schema.end_date
            )
            return data
        except SQLAlchemyError:
            logger.exception("Ошибка в функции inspection_per_day (SQLAlchemyError)")
            raise

    async def diseases_per_patient(self, disease_ids_: list[int]) -> list:
        try:
            data = await self._repository_inspection.get_unique_patients_count_by_disease_ids(
                disease_ids_
            )
            return data
        except SQLAlchemyError:
            logger.exception(
                f"Ошибка в функции diseases_per_patient с disease_ids_ = {disease_ids_}  (SQLAlchemyError)"
            )
            raise

    async def disease_per_patient(self, disease_id_: int) -> int:
        try:
            data = await self._repository_inspection.get_unique_patients_count_by_disease_id(
                disease_id_
            )
            return data
        except SQLAlchemyError:
            logger.exception(
                f"Ошибка пфункции disease_per_patient с disease_id_ = {disease_id_}  (SQLAlchemyError)"
            )
            raise
