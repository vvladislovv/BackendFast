"""Middleware для логирования запросов и ответов."""
import time
from litestar import Request, Response
from litestar.middleware import DefineMiddleware
from litestar.types import ASGIApp, Receive, Scope, Send

from utils.logger import get_logger

logger = get_logger()


class LoggingMiddleware:
    """Middleware для логирования всех HTTP запросов и ответов."""
    
    def __init__(self, app: ASGIApp) -> None:
        """Инициализация middleware."""
        self.app = app
    
    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """Обработка запроса."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # Получаем информацию о запросе
        method = scope["method"]
        path = scope["path"]
        client = scope.get("client", ["unknown", 0])
        client_ip = client[0] if client else "unknown"
        
        # Логируем начало запроса
        start_time = time.time()
        logger.info(f"→ {method} {path} from {client_ip}")
        
        # Переменная для хранения статус кода
        status_code = None
        
        async def send_wrapper(message):
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message["status"]
            await send(message)
        
        try:
            await self.app(scope, receive, send_wrapper)
        except Exception as e:
            # Логируем ошибку
            duration = time.time() - start_time
            logger.error(
                f"✗ {method} {path} - ERROR after {duration:.3f}s: {str(e)}",
                exc_info=True
            )
            raise
        else:
            # Логируем успешный ответ
            duration = time.time() - start_time
            
            if status_code:
                if 200 <= status_code < 300:
                    logger.info(f"← {method} {path} - {status_code} in {duration:.3f}s")
                elif 400 <= status_code < 500:
                    logger.warning(f"← {method} {path} - {status_code} in {duration:.3f}s")
                elif status_code >= 500:
                    logger.error(f"← {method} {path} - {status_code} in {duration:.3f}s")
                else:
                    logger.info(f"← {method} {path} - {status_code} in {duration:.3f}s")


def create_logging_middleware() -> DefineMiddleware:
    """Создает middleware для логирования."""
    return DefineMiddleware(LoggingMiddleware)
