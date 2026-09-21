from app.repository.patient import PatientRepository


class PatientService:
    def __init__(self, repository: PatientRepository):
        super().__init__(repository)
