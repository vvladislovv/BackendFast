"""Настройка логирования через Loguru."""
import sys
from pathlib import Path

from loguru import logger

from core.config import settings

# Удаляем стандартный handler
logger.remove()

# Создаем папку для логов
logs_dir = Path("logs")
logs_dir.mkdir(exist_ok=True)

# Логи в консоль
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level=settings.log_level,
    colorize=True,
)

# Логи в JSON файл
logger.add(
    logs_dir / "app_{time:YYYY-MM-DD}.json",
    format="{message}",
    level=settings.log_level,
    rotation=settings.log_rotation,
    retention=settings.log_retention,
    compression="zip",
    serialize=True,
)

# Логи ошибок отдельно
logger.add(
    logs_dir / "errors_{time:YYYY-MM-DD}.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} - {message}",
    level="ERROR",
    rotation=settings.log_rotation,
    retention=settings.log_retention,
    backtrace=True,
    diagnose=True,
)


def get_logger():
    """Получить настроенный logger."""
    return logger
