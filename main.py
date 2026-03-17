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
from api.static_files import StaticFilesController
from core.config import settings
from core.database import engine, get_db_session
from core.auth import APIKeyMiddleware
from middleware.logging_middleware import create_logging_middleware
from utils.logger import get_logger
from utils.exceptions import AppException, NotFoundException as CustomNotFoundException

logger = get_logger()


async def startup() -> None:
    logger.info("Запуск Backend API")
    
    # Проверяем и создаем директории для загрузок
    from pathlib import Path
    uploads_dir = Path("uploads")
    photos_dir = Path("uploads/photos")
    
    uploads_dir.mkdir(parents=True, exist_ok=True)
    photos_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"📂 Директория uploads: {uploads_dir.absolute()} (существует: {uploads_dir.exists()})")
    logger.info(f"📂 Директория photos: {photos_dir.absolute()} (существует: {photos_dir.exists()})")
    
    # Тестируем доступ к фотографиям
    try:
        from integrations.telegram.photo_handler import test_photo_access
        test_photo_access()
    except Exception as e:
        logger.error(f"Ошибка тестирования фото: {e}")
    
    # Добавляем security scheme в OpenAPI после инициализации
    if app.openapi_schema:
        if not hasattr(app.openapi_schema, 'components') or app.openapi_schema.components is None:
            from litestar.openapi.spec import Components
            app.openapi_schema.components = Components()
        if not hasattr(app.openapi_schema.components, 'security_schemes') or app.openapi_schema.components.security_schemes is None:
            app.openapi_schema.components.security_schemes = {}
        from litestar.openapi.spec import SecurityScheme
        app.openapi_schema.components.security_schemes["APIKeyHeader"] = SecurityScheme(
            type="apiKey",
            name="X-API-Key",
            security_scheme_in="header",
            description="API ключ для доступа. Используйте: internal-bot-key-2026"
        )
        # Добавляем security requirement глобально
        if not hasattr(app.openapi_schema, 'security') or app.openapi_schema.security is None:
            app.openapi_schema.security = []
        app.openapi_schema.security.append({"APIKeyHeader": []})
        
        # Убираем требование API ключа для публичных endpoints
        public_endpoints = [
            ('/api/v1/vacancies', 'get'),
            ('/api/v1/reviews', 'get'),
            ('/api/v1/articles', 'get'),
            ('/api/v1/cases', 'get'),
            ('/api/v1/applications', 'post'),
        ]
        
        if hasattr(app.openapi_schema, 'paths'):
            for path, method in public_endpoints:
                if path in app.openapi_schema.paths:
                    path_item = app.openapi_schema.paths[path]
                    if hasattr(path_item, method):
                        operation = getattr(path_item, method)
                        # Убираем security requirement для этого endpoint
                        operation.security = []
                        logger.info(f"Убрано требование API ключа для {method.upper()} {path}")
        
        # Кастомизируем схему для POST /api/v1/applications
        if hasattr(app.openapi_schema, 'paths') and '/api/v1/applications' in app.openapi_schema.paths:
            applications_path = app.openapi_schema.paths['/api/v1/applications']
            if hasattr(applications_path, 'post'):
                # Удаляем query параметры
                applications_path.post.parameters = []
                
                # Добавляем правильный requestBody для multipart/form-data
                applications_path.post.request_body = {
                    "content": {
                        "multipart/form-data": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "name": {
                                        "type": "string",
                                        "minLength": 1,
                                        "maxLength": 255,
                                        "description": "Имя клиента"
                                    },
                                    "email": {
                                        "type": "string",
                                        "format": "email",
                                        "description": "Email клиента"
                                    },
                                    "message": {
                                        "type": "string",
                                        "minLength": 1,
                                        "description": "Сообщение от клиента"
                                    },
                                    "company": {
                                        "type": "string",
                                        "maxLength": 255,
                                        "description": "Название компании (опционально)"
                                    },
                                    "phone": {
                                        "type": "string",
                                        "maxLength": 50,
                                        "description": "Телефон клиента (опционально)"
                                    },
                                    "file": {
                                        "type": "string",
                                        "format": "binary",
                                        "description": "Прикрепленный файл (опционально)"
                                    }
                                },
                                "required": ["name", "email", "message"]
                            }
                        }
                    },
                    "required": True
                }
                logger.info("OpenAPI схема для POST /api/v1/applications обновлена")


async def shutdown() -> None:
    await engine.dispose()
    logger.info("Остановка Backend API")


def app_exception_handler(request: Request, exc: AppException) -> Response:
    return Response(
        content={"status_code": exc.status_code, "detail": exc.message},
        status_code=exc.status_code
    )


def not_found_handler(request: Request, exc: NotFoundException) -> Response:
    return Response(
        content={"status_code": 404, "detail": "Ресурс не найден"},
        status_code=404
    )


def validation_error_handler(request: Request, exc: ValidationException) -> Response:
    return Response(
        content={"status_code": 400, "detail": "Ошибка валидации"},
        status_code=400
    )


def internal_server_error_handler(request: Request, exc: Exception) -> Response:
    import traceback
    logger.error(traceback.format_exc())
    return Response(
        content={"status_code": 500, "detail": "Внутренняя ошибка сервера"},
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
        StaticFilesController,
    ],
    dependencies={"db_session": get_db_session},
    middleware=[APIKeyMiddleware, create_logging_middleware()],
    exception_handlers={
        AppException: app_exception_handler,
        NotFoundException: not_found_handler,
        ValidationException: validation_error_handler,
        Exception: internal_server_error_handler,
    },
    openapi_config=OpenAPIConfig(
        title="Backend API",
        version="1.0.0",
        description="""
        # Backend API для управления контентом
        
        ## Аутентификация
        Большинство эндпоинтов требуют API ключ в заголовке запроса:
        ```
        X-API-Key: internal-bot-key-2026
        ```
        
        Используйте кнопку **Authorize** справа вверху, чтобы ввести API ключ один раз для всех запросов.
        
        ## 🔓 Эндпоинты БЕЗ API ключа (публичные)
        - `GET /api/v1/vacancies` - получить список вакансий
        - `GET /api/v1/reviews` - получить список отзывов
        - `GET /api/v1/articles` - получить список статей
        - `GET /api/v1/cases` - получить список кейсов
        - `POST /api/v1/applications` - создание заявки (доступно с фронтенда)
        
        ## 🔒 Эндпоинты С API ключом (защищенные)
        Все остальные операции требуют API ключ:
        - Создание, обновление, удаление записей
        - Получение отдельных записей по ID
        - Изменение рейтинга и видимости
        
        ## Основные сущности
        - **Vacancies** - вакансии компании
        - **Reviews** - отзывы клиентов
        - **Articles** - статьи блога
        - **Cases** - портфолио проектов
        - **Applications** - заявки от клиентов
        
        ## Общие параметры
        - **rating** - рейтинг для сортировки (целое число, по умолчанию 0)
        - **is_hidden** - флаг видимости (true/false)
        - **is_fresh** - флаг свежести для кейсов (true/false)
        """,
        use_handler_docstrings=False,
    ),
    on_startup=[startup],
    on_shutdown=[shutdown],
    debug=True,
)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=settings.host, port=settings.port, reload=settings.debug)
