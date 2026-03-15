"""Аутентификация через API ключи."""
from litestar import Request
from litestar.exceptions import NotAuthorizedException
from litestar.middleware.base import AbstractMiddleware

from core.config import settings
from utils.logger import get_logger

logger = get_logger()


# Список разрешенных API ключей
ALLOWED_API_KEYS = [
    settings.secret_key,  # Основной ключ из .env
    "internal-bot-key-2026",  # Ключ для бота
]


class APIKeyMiddleware(AbstractMiddleware):
    """Middleware для проверки API ключей."""
    
    async def __call__(self, scope, receive, send) -> None:
        """Проверяет API ключ перед обработкой запроса."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        path = scope.get("path", "")
        method = scope.get("method", "")
        
        logger.info(f"APIKeyMiddleware: {method} {path}")
        
        # Пропускаем health check и root
        if path in ["/health", "/"]:
            logger.info("Пропускаем health/root")
            await self.app(scope, receive, send)
            return
        
        # Пропускаем Swagger UI
        if path.startswith("/schema"):
            logger.info("Пропускаем schema")
            await self.app(scope, receive, send)
            return
        
        # Пропускаем статические файлы (фотографии)
        if path.startswith("/uploads"):
            logger.info("Пропускаем статические файлы")
            await self.app(scope, receive, send)
            return
        
        # Пропускаем endpoint для создания заявок (доступен с фронтенда)
        if path == "/api/v1/applications" and method == "POST":
            logger.info("Пропускаем проверку API ключа для POST /api/v1/applications")
            await self.app(scope, receive, send)
            return
        
        # Все остальные запросы к /applications требуют API ключ
        if path.startswith("/api/v1/applications"):
            logger.info(f"Проверка API ключа для {method} {path}")
        
        # Проверяем API ключ
        headers = dict(scope.get("headers", []))
        api_key = headers.get(b"x-api-key", b"").decode()
        
        if not api_key:
            logger.warning(f"Попытка доступа без API ключа: {path}")
            response_body = '{"detail":"API ключ не предоставлен. Используйте заголовок X-API-Key"}'.encode('utf-8')
            await send({
                "type": "http.response.start",
                "status": 401,
                "headers": [
                    [b"content-type", b"application/json; charset=utf-8"],
                    [b"content-length", str(len(response_body)).encode()],
                ],
            })
            await send({
                "type": "http.response.body",
                "body": response_body,
            })
            return
        
        if api_key not in ALLOWED_API_KEYS:
            logger.warning(f"Попытка доступа с неверным API ключом: {path}")
            response_body = '{"detail":"Неверный API ключ"}'.encode('utf-8')
            await send({
                "type": "http.response.start",
                "status": 401,
                "headers": [
                    [b"content-type", b"application/json; charset=utf-8"],
                    [b"content-length", str(len(response_body)).encode()],
                ],
            })
            await send({
                "type": "http.response.body",
                "body": response_body,
            })
            return
        
        logger.info(f"Доступ разрешен с API ключом для: {path}")
        await self.app(scope, receive, send)
