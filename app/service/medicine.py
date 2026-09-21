from app.repository.medicine import MedicineRepository
from app.service.base import BaseService


class MedicineService(BaseService):
    def __init__(self, repository: MedicineRepository):
        super().__init__(repository)
