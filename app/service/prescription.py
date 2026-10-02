from app.core.model import Prescription
from app.repository.prescription import PrescriptionRepository
from app.service.base import BaseService


class PrescriptionService(BaseService):
    def __init__(self, repository: PrescriptionRepository):
        super().__init__(repository, Prescription)
