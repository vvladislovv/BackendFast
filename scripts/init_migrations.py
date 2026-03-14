"""Скрипт для инициализации миграций БД."""
import asyncio
from sqlalchemy import text
from core.database import engine
from models.base import Base
from utils.logger import get_logger

# Импортируем все модели чтобы они зарегистрировались в Base.metadata
from models.vacancy import Vacancy
from models.review import Review
from models.article import Article
from models.case import Case

logger = get_logger()


async def init_db():
    """Создание всех таблиц в БД."""
    try:
        logger.info("Начало инициализации БД...")
        
        async with engine.begin() as conn:
            # Создание всех таблиц
            await conn.run_sync(Base.metadata.create_all)
            
        logger.info("БД успешно инициализирована!")
        
    except Exception as e:
        logger.error(f"Ошибка при инициализации БД: {e}")
        raise
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(init_db())
