"""Главный файл приложения Litestar."""
from litestar import Litestar, Request, Response
from litestar.openapi import OpenAPIConfig
from litestar.status_codes import HTTP_500_INTERNAL_SERVER_ERROR
from litestar.exceptions import HTTPException, NotFoundException, ValidationException

from api.health import health_check, root
from api.v1.vacancies import VacancyController
from api.v1.reviews import ReviewController
from api.v1.articles import ArticleController
from api.v1.cases import CaseController
from api.v1.applications import ApplicationController
from api.v1.upload import UploadController
from core.config import settings
from core.database import engine, get_db_session
from core.auth import APIKeyMiddleware
from middleware.logging_middleware import create_logging_middleware
from utils.logger import get_logger
from utils.exceptions import AppException, NotFoundException as CustomNotFoundException

logger = get_logger()


async def startup() -> None:
    """Действия при запуске приложения."""
    logger.info("=" * 60)
    logger.info("Запуск приложения Backend API")
    logger.info(f"Debug режим: {settings.debug}")
    logger.info(f"Host: {settings.host}:{settings.port}")
    logger.info(f"Database: {settings.database_url.split('@')[-1] if '@' in settings.database_url else 'configured'}")
    logger.info("=" * 60)


async def shutdown() -> None:
    """Действия при остановке приложения."""
    logger.info("=" * 60)
    logger.info("Остановка приложения...")
    await engine.dispose()
    logger.info("База данных отключена")
    logger.info("=" * 60)


def app_exception_handler(request: Request, exc: AppException) -> Response:
    """Обработчик кастомных исключений приложения."""
    try:
        method = getattr(request, 'method', 'UNKNOWN')
        path = getattr(request.url, 'path', 'UNKNOWN') if hasattr(request, 'url') else 'UNKNOWN'
    except:
        method = 'UNKNOWN'
        path = 'UNKNOWN'
    
    logger.warning(f"{exc.status_code} {exc.__class__.__name__}: {method} {path} - {exc.message}")
    return Response(
        content={
            "status_code": exc.status_code,
            "detail": exc.message,
            "error": exc.__class__.__name__
        },
        status_code=exc.status_code
    )


def not_found_handler(request: Request, exc: NotFoundException) -> Response:
    """Обработчик ошибки 404."""
    try:
        method = getattr(request, 'method', 'UNKNOWN')
        path = getattr(request.url, 'path', 'UNKNOWN') if hasattr(request, 'url') else 'UNKNOWN'
    except:
        method = 'UNKNOWN'
        path = 'UNKNOWN'
    
    logger.warning(f"404 Not Found: {method} {path}")
    return Response(
        content={
            "status_code": 404,
            "detail": f"Ресурс не найден: {path}",
            "error": "Not Found"
        },
        status_code=404
    )


def validation_error_handler(request: Request, exc: ValidationException) -> Response:
    """Обработчик ошибок валидации."""
    try:
        method = getattr(request, 'method', 'UNKNOWN')
        path = getattr(request.url, 'path', 'UNKNOWN') if hasattr(request, 'url') else 'UNKNOWN'
    except:
        method = 'UNKNOWN'
        path = 'UNKNOWN'
    
    logger.warning(f"400 Validation Error: {method} {path} - {exc.detail}")
    return Response(
        content={
            "status_code": 400,
            "detail": "Ошибка валидации данных",
            "errors": exc.extra if hasattr(exc, 'extra') else str(exc.detail),
            "error": "Validation Error"
        },
        status_code=400
    )


def internal_server_error_handler(request: Request, exc: Exception) -> Response:
    """Обработчик внутренних ошибок сервера."""
    import traceback
    error_details = traceback.format_exc()
    
    # Безопасное получение метода и пути
    try:
        method = getattr(request, 'method', 'UNKNOWN')
        path = getattr(request.url, 'path', 'UNKNOWN') if hasattr(request, 'url') else 'UNKNOWN'
    except:
        method = 'UNKNOWN'
        path = 'UNKNOWN'
    
    # Логируем без форматирования чтобы избежать KeyError
    logger.error(f"500 Internal Server Error: {method} {path}")
    logger.error(error_details)
    
    return Response(
        content={
            "status_code": 500,
            "detail": "Внутренняя ошибка сервера",
            "error": "Internal Server Error",
            "traceback": error_details if settings.debug else None
        },
        status_code=HTTP_500_INTERNAL_SERVER_ERROR
    )


app = Litestar(
    route_handlers=[
        root,
        health_check,
        VacancyController,
        ReviewController,
        ArticleController,
        CaseController,
        ApplicationController,
        UploadController,
    ],
    dependencies={"db_session": get_db_session},
    middleware=[
        APIKeyMiddleware,  # Проверка API ключей
        create_logging_middleware(),  # Логирование
    ],
    exception_handlers={
        AppException: app_exception_handler,
        NotFoundException: not_found_handler,
        ValidationException: validation_error_handler,
        Exception: internal_server_error_handler,
    },
    openapi_config=OpenAPIConfig(
        title="Backend API - Управление контентом",
        version="1.0.0",
        description="""
# Backend API для управления контентом

Полнофункциональный REST API для управления:
- 💼 **Вакансиями** - создание, редактирование, управление рейтингом
- ⭐ **Отзывами** - отзывы клиентов с рейтингом 1-5 звезд
- 📰 **Статьями** - публикации и новости
- 💡 **Кейсами** - портфолио проектов с тегами

## Основные возможности

### CRUD операции
Все сущности поддерживают полный набор операций:
- `POST` - Создание новой записи
- `GET` - Получение списка или одной записи
- `PUT` - Полное обновление записи
- `PATCH` - Частичное обновление (рейтинг, видимость)
- `DELETE` - Удаление записи

### Управление видимостью
Каждая сущность может быть скрыта/показана через `PATCH /{id}/hide`

### Система рейтинга
Управление рейтингом через `PATCH /{id}/rating`

### Специальные функции
- **Кейсы**: Пометка как "свежий" и получение только свежих кейсов
- **Отзывы**: Рейтинг 1-5 звезд

## Коды ответов

- `200 OK` - Успешная операция
- `201 Created` - Ресурс успешно создан
- `400 Bad Request` - Ошибка валидации данных
- `404 Not Found` - Ресурс не найден
- `500 Internal Server Error` - Внутренняя ошибка сервера

## Безопасность

- ✅ Валидация всех входных данных
- ✅ Защита от SQL injection через ORM
- ✅ Ограничения длины полей
- ✅ Типизация данных через Pydantic

## База данных

PostgreSQL с async SQLAlchemy ORM
        """,
        contact={
            "name": "API Support",
            "email": "support@example.com"
        },
        use_handler_docstrings=True,
        tags=[
            {"name": "Health", "description": "Проверка состояния API"},
            {"name": "Vacancies", "description": "💼 Управление вакансиями"},
            {"name": "Reviews", "description": "⭐ Управление отзывами клиентов"},
            {"name": "Articles", "description": "📰 Управление статьями и публикациями"},
            {"name": "Cases", "description": "💡 Управление кейсами и портфолио"},
        ],
    ),
    on_startup=[startup],
    on_shutdown=[shutdown],
    debug=True,  # Включаем debug для полного traceback
)


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )
