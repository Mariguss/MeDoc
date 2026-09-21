from app.repository.prescription import PrescriptionRepository


class PrescriptionService:
    def __init__(self, repository: PrescriptionRepository):
        super().__init__(repository)
