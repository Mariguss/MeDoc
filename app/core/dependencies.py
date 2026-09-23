from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import database
from app.repository.disease import DiseaseRepository
from app.repository.employee import EmployeeRepository
from app.repository.inspection import InspectionRepository
from app.repository.medicine import MedicineRepository
from app.repository.patient import PatientRepository
from app.repository.prescription import PrescriptionRepository
from app.service.employee import EmployeeService
from app.service.inspection import InspectionService
from app.service.medicine import MedicineService
from app.service.patient import PatientService


async def get_employee_repository(
    session: AsyncSession = Depends(database.get_session),
) -> EmployeeRepository:
    return EmployeeRepository(session)


async def get_employee_service(
    repo: EmployeeRepository = Depends(get_employee_repository),
) -> EmployeeService:
    return EmployeeService(repo)


async def get_patient_repository(
    session: AsyncSession = Depends(database.get_session),
) -> PatientRepository:
    return PatientRepository(session)


async def get_patient_service(
    repo: PatientRepository = Depends(get_patient_repository),
) -> PatientService:
    return PatientService(repo)


async def get_medicine_repository(
    session: AsyncSession = Depends(database.get_session),
) -> MedicineRepository:
    return MedicineRepository(session)


async def get_medicine_service(
    repo: MedicineRepository = Depends(get_medicine_repository),
) -> MedicineService:
    return MedicineService(repo)


async def get_inspection_repository(
    session: AsyncSession = Depends(database.get_session),
) -> InspectionRepository:
    return InspectionRepository(session)

async def get_disease_repository(
        session: AsyncSession = Depends(database.get_session),
) -> DiseaseRepository:
    return DiseaseRepository(session)

async def get_prescription_repository(
        session: AsyncSession = Depends(database.get_session),
) -> PrescriptionRepository:
    return PrescriptionRepository(session)

async def get_inspection_service(
    repo_inspection: InspectionRepository = Depends(get_inspection_repository),
    repo_employee: EmployeeRepository = Depends(get_employee_repository),
    repo_patient: PatientRepository = Depends(get_patient_repository),
    repo_disease: DiseaseRepository = Depends(get_disease_repository),
    repo_prescription: PrescriptionRepository = Depends(get_prescription_repository),


) -> InspectionService:
    return InspectionService(
        repo_inspection,
        repo_employee,
        repo_patient,
        repo_disease,
        repo_prescription,
    )
