"""Pytest конфигурация и фикстуры."""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from core.database import Base, get_db_session
from main import app

TEST_DATABASE_URL = "postgresql+asyncpg://test:test@localhost:5432/test_db"

engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(scope="function")
async def db_session():
    """Фикстура для тестовой сессии БД."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with TestSessionLocal() as session:
        yield session
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
async def client(db_session):
    """Фикстура для тестового клиента."""
    
    async def override_get_db():
        yield db_session
    
    app.dependencies["db_session"] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
