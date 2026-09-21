class DuplicatedError(Exception):
    """Выбрасывается при нарушении уникальности (дубликат)."""
    def __init__(self, detail: str = "Record already exists"):
        self.detail = detail
        super().__init__(self.detail)

class RelationshipViolationError(Exception):
    """Выбрасывается при попытке нарушить связи (FK) или удалить зависимую запись."""
    def __init__(self, detail: str = "Cannot perform operation due to relationship constraints"):
        self.detail = detail
        super().__init__(self.detail)

class NotFoundError(Exception):
    """Выбрасывается, когда ресурс не найден."""
    def __init__(self, detail: str = "Resource not found"):
        self.detail = detail
        super().__init__(self.detail)

class AuthError(Exception):
    """Выбрасывается при проблемах с авторизацией/аутентификацией."""
    def __init__(self, detail: str = "Authentication failed"):
        self.detail = detail
        super().__init__(self.detail)

class WrongCredentialsError(AuthError):
    """Частный случай AuthError."""
    def __init__(self, detail: str = "Invalid username or password"):
        super().__init__(detail)

class ValidationError(Exception):
    """Выбрасывается при ошибке валидации данных (не Pydantic)."""
    def __init__(self, detail: str = "Invalid data provided"):
        self.detail = detail
        super().__init__(self.detail)
