from app.repository.patient import PatientRepository
from app.service.base import BaseService


class PatientService(BaseService):
    def __init__(self, repository: PatientRepository):
        super().__init__(repository)
