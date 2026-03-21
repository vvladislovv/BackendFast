"""Пересоздание базы данных с новой структурой."""
import asyncio
import sys
from pathlib import Path

# Добавляем корневую директорию в путь
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import create_async_engine
from core.config import settings
from core.database import Base

# Импортируем все модели
from models.vacancy import Vacancy
from models.review import Review
from models.article import Article
from models.case import Case
from models.application import Application


async def recreate_database():
    """Пересоздать базу данных."""
    print("🔄 Пересоздание базы данных...")
    print(f"📊 Database URL: {settings.database_url}")
    
    engine = create_async_engine(settings.database_url, echo=True)
    
    try:
        async with engine.begin() as conn:
            print("\n🗑️  Удаление всех таблиц...")
            await conn.run_sync(Base.metadata.drop_all)
            print("✅ Таблицы удалены")
            
            print("\n📦 Создание новых таблиц...")
            await conn.run_sync(Base.metadata.create_all)
            print("✅ Таблицы созданы")
        
        print("\n✅ База данных успешно пересоздана!")
        print("\n📋 Созданные таблицы:")
        print("   - vacancies")
        print("   - reviews")
        print("   - articles (с полем content для Markdown)")
        print("   - cases")
        print("   - applications")
        
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        raise
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(recreate_database())
