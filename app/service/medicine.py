from app.repository.medicine import MedicineRepository


class MedicineService:
    def __init__(self, repository: MedicineRepository):
        super().__init__(repository)
