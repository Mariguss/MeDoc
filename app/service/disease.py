from app.repository.disease import DiseaseRepository
from app.service.base import BaseService


class DiseaseService(BaseService):
    def __init__(self, repository: DiseaseRepository):
        super().__init__(repository)
