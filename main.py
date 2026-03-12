"""Главный файл приложения Litestar."""
from litestar import Litestar
from litestar.contrib.sqlalchemy.plugins import SQLAlchemyAsyncConfig, SQLAlchemyPlugin
from litestar.openapi import OpenAPIConfig

from api.health import health_check, root
from api.v1.vacancies import VacancyController
from api.v1.reviews import ReviewController
from api.v1.articles import ArticleController
from api.v1.cases import CaseController
from core.config import settings
from core.database import engine, get_db_session
from middleware.error_handler import exception_handler
from utils.logger import get_logger

logger = get_logger()


sqlalchemy_config = SQLAlchemyAsyncConfig(
    connection_string=settings.database_url,
    session_dependency_key="db_session",
)


app = Litestar(
    route_handlers=[
        root,
        health_check,
        VacancyController,
        ReviewController,
        ArticleController,
        CaseController,
    ],
    dependencies={"db_session": get_db_session},
    plugins=[SQLAlchemyPlugin(config=sqlalchemy_config)],
    exception_handlers={Exception: exception_handler},
    openapi_config=OpenAPIConfig(
        title="Backend API",
        version="1.0.0",
        description="API для управления вакансиями, отзывами, статьями и кейсами",
    ),
    debug=settings.debug,
)


@app.on_startup
async def startup() -> None:
    """Действия при запуске приложения."""
    logger.info("Запуск приложения...")
    logger.info(f"Debug режим: {settings.debug}")
    logger.info(f"Host: {settings.host}:{settings.port}")


@app.on_shutdown
async def shutdown() -> None:
    """Действия при остановке приложения."""
    logger.info("Остановка приложения...")
    await engine.dispose()


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )
