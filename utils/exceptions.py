"""Кастомные исключения приложения."""


class AppException(Exception):
    """Базовое исключение приложения."""
    
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class NotFoundException(AppException):
    """Ресурс не найден."""
    
    def __init__(self, message: str = "Ресурс не найден"):
        super().__init__(message, status_code=404)


class ValidationException(AppException):
    """Ошибка валидации данных."""
    
    def __init__(self, message: str = "Ошибка валидации данных"):
        super().__init__(message, status_code=422)


class UnauthorizedException(AppException):
    """Ошибка авторизации."""
    
    def __init__(self, message: str = "Не авторизован"):
        super().__init__(message, status_code=401)


class ForbiddenException(AppException):
    """Доступ запрещен."""
    
    def __init__(self, message: str = "Доступ запрещен"):
        super().__init__(message, status_code=403)


class DatabaseException(AppException):
    """Ошибка базы данных."""
    
    def __init__(self, message: str = "Ошибка базы данных"):
        super().__init__(message, status_code=500)
