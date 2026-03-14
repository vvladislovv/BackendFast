"""Сервис для работы с заявками."""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.application import Application
from schemas.application import ApplicationCreate


class ApplicationService:
    """Сервис для работы с заявками."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, data: ApplicationCreate) -> Application:
        """Создать заявку."""
        application = Application(**data.model_dump())
        self.session.add(application)
        await self.session.commit()
        await self.session.refresh(application)
        return application
    
    async def get_all(self, status: str | None = None) -> list[Application]:
        """Получить все заявки."""
        query = select(Application).order_by(Application.created_at.desc())
        if status:
            query = query.where(Application.status == status)
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def get_by_id(self, application_id: int) -> Application | None:
        """Получить заявку по ID."""
        result = await self.session.execute(
            select(Application).where(Application.id == application_id)
        )
        return result.scalar_one_or_none()
    
    async def update_status(self, application_id: int, status: str) -> Application | None:
        """Обновить статус заявки."""
        application = await self.get_by_id(application_id)
        if application:
            application.status = status
            await self.session.commit()
            await self.session.refresh(application)
        return application
    
    async def delete(self, application_id: int) -> bool:
        """Удалить заявку."""
        application = await self.get_by_id(application_id)
        if application:
            await self.session.delete(application)
            await self.session.commit()
            return True
        return False
