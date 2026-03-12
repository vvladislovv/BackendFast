"""Middleware для обработки ошибок."""
from litestar import Request, Response
from litestar.exceptions import HTTPException
from litestar.status_codes import HTTP_500_INTERNAL_SERVER_ERROR

from utils.exceptions import AppException
from utils.logger import get_logger

logger = get_logger()


async def exception_handler(request: Request, exc: Exception) -> Response:
    """Глобальный обработчик исключений."""
    
    if isinstance(exc, AppException):
        logger.error(f"AppException: {exc.message}", exc_info=True)
        return Response(
            content={"error": exc.message},
            status_code=exc.status_code,
        )
    
    if isinstance(exc, HTTPException):
        logger.error(f"HTTPException: {exc.detail}", exc_info=True)
        return Response(
            content={"error": exc.detail},
            status_code=exc.status_code,
        )
    
    logger.error(f"Неожиданная ошибка: {str(exc)}", exc_info=True)
    return Response(
        content={"error": "Внутренняя ошибка сервера"},
        status_code=HTTP_500_INTERNAL_SERVER_ERROR,
    )
