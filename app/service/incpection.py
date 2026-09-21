from app.repository.incpection import InspectionRepository


class InspectionService:
    def __init__(self, repository: InspectionRepository):
        super().__init__(repository)
