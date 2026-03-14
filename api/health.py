"""Health check endpoint."""
from litestar import get
from litestar.status_codes import HTTP_200_OK

from utils.logger import get_logger

logger = get_logger()


@get(
    "/health",
    tags=["Health"],
    summary="Проверка здоровья API",
    description="""
    Проверяет доступность и работоспособность API.
    
    **Ответ:**
    - `200` - API работает нормально
    
    **Использование:** Для мониторинга и health checks
    """,
    status_code=HTTP_200_OK,
)
async def health_check() -> dict[str, str]:
    """
    Health check endpoint.
    
    Returns:
        Status информация о приложении
    """
    logger.info("Health check запрос")
    return {
        "status": "healthy",
        "service": "backend-api",
        "version": "1.0.0"
    }


@get(
    "/",
    tags=["Health"],
    summary="Корневой endpoint",
    description="""
    Возвращает информацию об API и ссылки на документацию.
    
    **Ответ:**
    - `200` - Информация об API
    """,
    status_code=HTTP_200_OK,
)
async def root() -> dict[str, str]:
    """
    Root endpoint.
    
    Returns:
        Приветственное сообщение
    """
    return {
        "message": "Backend API",
        "docs": "/schema/swagger",
        "health": "/health"
    }
