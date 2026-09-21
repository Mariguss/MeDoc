from app.repository.disease import DiseaseRepository


class DiseaseService:
    def __init__(self, repository: DiseaseRepository):
        super().__init__(repository)
