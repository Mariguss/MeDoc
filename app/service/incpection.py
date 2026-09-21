from app.repository.incpection import InspectionRepository
from app.service.base import BaseService


class InspectionService(BaseService):
    def __init__(self, repository: InspectionRepository):
        super().__init__(repository)
