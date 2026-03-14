"""API endpoints для заявок с сайта."""
import asyncio
from litestar import Controller, get, post, patch, delete
from litestar.di import Provide
from litestar.params import Parameter
from litestar.exceptions import NotFoundException
from sqlalchemy.ext.asyncio import AsyncSession

from schemas.application import ApplicationCreate, ApplicationResponse
from models.application import Application
from utils.logger import get_logger
from sqlalchemy import select
from integrations.telegram.application_notifier import notify_new_application

logger = get_logger()


async def get_db(db_session: AsyncSession) -> AsyncSession:
    """Получить сессию БД."""
    return db_session


class ApplicationController(Controller):
    """Контроллер для работы с заявками."""
    
    path = "/api/v1/applications"
    tags = ["Applications"]
    
    @post(
        "/",
        summary="Создать заявку",
        description="Создание новой заявки с сайта. Доступен без API ключа.",
        status_code=201,
    )
    async def create_application(
        self, 
        data: ApplicationCreate, 
        db_session: AsyncSession,
    ) -> ApplicationResponse:
        """Создать заявку с сайта."""
        try:
            logger.info(f"Создание заявки от {data.email}")
            
            # Создаем заявку напрямую
            application = Application(
                name=data.name,
                company=data.company,
                email=data.email,
                phone=data.phone,
                message=data.message,
                file_path=data.file_path,
                status="new"
            )
            
            db_session.add(application)
            await db_session.commit()
            await db_session.refresh(application)
            
            logger.info(f"Заявка создана: ID={application.id}")
            
            # Отправляем уведомление в Telegram (асинхронно, не блокируем ответ)
            try:
                asyncio.create_task(notify_new_application({
                    "id": application.id,
                    "name": application.name,
                    "company": application.company,
                    "email": application.email,
                    "phone": application.phone,
                    "message": application.message,
                    "file_path": application.file_path
                }))
            except Exception as e:
                logger.error(f"Ошибка создания задачи уведомления: {e}")
            
            return ApplicationResponse.model_validate(application)
            
        except Exception as e:
            logger.error(f"Ошибка создания заявки: {e}", exc_info=True)
            await db_session.rollback()
            raise
    
    @get(
        "/",
        summary="Получить все заявки",
        description="Получить список всех заявок. Требует API ключ.",
    )
    async def get_applications(
        self,
        db_session: AsyncSession,
        status: str | None = Parameter(
            default=None,
            query="status",
            description="Фильтр по статусу (new, read, processed)"
        ),
    ) -> list[ApplicationResponse]:
        """Получить все заявки."""
        try:
            logger.info(f"Получение списка заявок, фильтр: {status}")
            
            query = select(Application).order_by(Application.created_at.desc())
            if status:
                query = query.where(Application.status == status)
            
            result = await db_session.execute(query)
            applications = list(result.scalars().all())
            
            logger.info(f"Найдено заявок: {len(applications)}")
            return [ApplicationResponse.model_validate(app) for app in applications]
            
        except Exception as e:
            logger.error(f"Ошибка получения заявок: {e}", exc_info=True)
            raise
    
    @get(
        "/{application_id:int}",
        summary="Получить заявку по ID",
        description="Получить конкретную заявку по её ID. Требует API ключ.",
    )
    async def get_application(
        self, 
        application_id: int, 
        db_session: AsyncSession,
    ) -> ApplicationResponse:
        """Получить заявку по ID."""
        try:
            logger.info(f"Получение заявки ID={application_id}")
            
            result = await db_session.execute(
                select(Application).where(Application.id == application_id)
            )
            application = result.scalar_one_or_none()
            
            if not application:
                logger.warning(f"Заявка ID={application_id} не найдена")
                raise NotFoundException(detail=f"Заявка с ID {application_id} не найдена")
            
            return ApplicationResponse.model_validate(application)
            
        except NotFoundException:
            raise
        except Exception as e:
            logger.error(f"Ошибка получения заявки: {e}", exc_info=True)
            raise
    
    @patch(
        "/{application_id:int}/status",
        summary="Изменить статус заявки",
        description="Изменить статус заявки (new, read, processed). Требует API ключ.",
    )
    async def update_status(
        self,
        application_id: int,
        db_session: AsyncSession,
        status: str = Parameter(query="status", description="Новый статус"),
    ) -> ApplicationResponse:
        """Изменить статус заявки."""
        try:
            logger.info(f"Обновление статуса заявки ID={application_id} на {status}")
            
            result = await db_session.execute(
                select(Application).where(Application.id == application_id)
            )
            application = result.scalar_one_or_none()
            
            if not application:
                logger.warning(f"Заявка ID={application_id} не найдена")
                raise NotFoundException(detail=f"Заявка с ID {application_id} не найдена")
            
            application.status = status
            await db_session.commit()
            await db_session.refresh(application)
            
            logger.info(f"Статус заявки ID={application_id} обновлен на {status}")
            return ApplicationResponse.model_validate(application)
            
        except NotFoundException:
            raise
        except Exception as e:
            logger.error(f"Ошибка обновления статуса: {e}", exc_info=True)
            await db_session.rollback()
            raise
    
    @delete(
        "/{application_id:int}",
        summary="Удалить заявку",
        description="Удалить заявку по ID. Требует API ключ.",
        status_code=204,
    )
    async def delete_application(
        self, 
        application_id: int, 
        db_session: AsyncSession,
    ) -> None:
        """Удалить заявку."""
        try:
            logger.info(f"Удаление заявки ID={application_id}")
            
            result = await db_session.execute(
                select(Application).where(Application.id == application_id)
            )
            application = result.scalar_one_or_none()
            
            if not application:
                logger.warning(f"Заявка ID={application_id} не найдена")
                raise NotFoundException(detail=f"Заявка с ID {application_id} не найдена")
            
            await db_session.delete(application)
            await db_session.commit()
            
            logger.info(f"Заявка ID={application_id} удалена")
            
        except NotFoundException:
            raise
        except Exception as e:
            logger.error(f"Ошибка удаления заявки: {e}", exc_info=True)
            await db_session.rollback()
            raise
