"""API endpoints для заявок."""
import asyncio
import os
import uuid
from pathlib import Path
from litestar import Controller, get, post, patch, delete, Request
from litestar.di import Provide
from litestar.params import Parameter, Body
from litestar.datastructures import UploadFile
from litestar.enums import RequestEncodingType
from litestar.exceptions import NotFoundException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from schemas.application import ApplicationCreate, ApplicationResponse
from models.application import Application
from utils.logger import get_logger
from integrations.telegram.application_notifier import notify_new_application

logger = get_logger()

# Директория для хранения файлов
UPLOAD_DIR = Path("/app/uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


class ApplicationController(Controller):
    path = "/api/v1/applications"
    tags = ["Applications"]
    
    @post(
        "/",
        summary="Создать заявку с файлом (для Swagger UI)",
        description="""
        Создание новой заявки от клиента с возможностью прикрепления файла.
        
        **Используйте этот эндпоинт в Swagger UI!**
        
        **Параметры (form-data):**
        - **name** (обязательно): Имя клиента (1-255 символов)
        - **email** (обязательно): Email клиента
        - **message** (обязательно): Сообщение от клиента
        - **company** (опционально): Название компании
        - **phone** (опционально): Телефон клиента
        - **file** (опционально): Прикрепленный файл (любой формат)
        
        **В Swagger UI:**
        1. Нажмите "Try it out"
        2. Заполните поля name, email, message
        3. Нажмите "Choose File" для загрузки файла
        4. Нажмите "Execute"
        
        **Через curl:**
        ```bash
        curl -X POST "http://localhost:8000/api/v1/applications/" \\
          -F "name=Иван Иванов" \\
          -F "email=ivan@example.com" \\
          -F "message=Хочу откликнуться" \\
          -F "company=ООО Компания" \\
          -F "phone=+7 999 123-45-67" \\
          -F "file=@resume.pdf"
        ```
        
        **Ответ:** Созданная заявка со статусом "new" и путем к файлу (если был прикреплен)
        """,
        status_code=201,
        security=[]
    )
    async def create_application(
        self,
        request: Request,
        db_session: AsyncSession
    ) -> ApplicationResponse:
        # Получаем данные из form-data
        form_data = await request.form()
        
        name = form_data.get("name")
        email = form_data.get("email")
        message = form_data.get("message")
        company = form_data.get("company")
        phone = form_data.get("phone")
        file = form_data.get("file")
        
        logger.info(f"POST /api/v1/applications от {email}")
        logger.info(f"Получен файл: {file is not None}, тип: {type(file) if file else 'None'}")
        
        # Обработка файла
        file_path = None
        if file and isinstance(file, UploadFile) and file.filename:
            try:
                logger.info(f"Загрузка файла: {file.filename}")
                
                # Генерируем уникальное имя
                file_ext = Path(file.filename).suffix
                unique_filename = f"{uuid.uuid4()}{file_ext}"
                file_full_path = UPLOAD_DIR / unique_filename
                
                # Читаем и сохраняем файл
                content = await file.read()
                logger.info(f"Прочитано байт: {len(content)}")
                
                with open(file_full_path, "wb") as f:
                    f.write(content)
                
                file_path = str(file_full_path)
                logger.info(f"Файл сохранен: {file_path}")
            except Exception as e:
                logger.error(f"Ошибка сохранения файла: {e}", exc_info=True)
        else:
            logger.info("Файл не передан или пустой")
        
        # Валидация данных через Pydantic
        try:
            validated_data = ApplicationCreate(
                name=name,
                email=email,
                message=message,
                company=company,
                phone=phone
            )
        except Exception as e:
            logger.error(f"Ошибка валидации: {e}")
            from litestar.exceptions import ValidationException
            raise ValidationException(detail=f"Ошибка валидации данных: {str(e)}")
        
        application = Application(
            name=validated_data.name,
            company=validated_data.company,
            email=validated_data.email,
            phone=validated_data.phone,
            message=validated_data.message,
            file_path=file_path,
            status="new"
        )
        
        db_session.add(application)
        await db_session.commit()
        await db_session.refresh(application)
        
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
            logger.error(f"Ошибка уведомления: {e}")
        
        return ApplicationResponse.model_validate(application)
    
    @get(
        "/",
        summary="Получить все заявки",
        description="""
        Получение списка всех заявок, отсортированных по дате создания (новые первыми).
        
        **Требуется API ключ:** X-API-Key: internal-bot-key-2026
        
        **Ответ:** Массив всех заявок с полной информацией
        """
    )
    async def get_applications(self, db_session: AsyncSession) -> list[ApplicationResponse]:
        logger.info("GET /api/v1/applications")
        result = await db_session.execute(select(Application).order_by(Application.created_at.desc()))
        applications = list(result.scalars().all())
        return [ApplicationResponse.model_validate(app) for app in applications]
    
    @get(
        "/{application_id:int}",
        summary="Получить заявку по ID",
        description="""
        Получение конкретной заявки по её ID.
        
        **Параметры пути:**
        - **application_id**: ID заявки (целое число)
        
        **Требуется API ключ:** X-API-Key: internal-bot-key-2026
        
        **Ответ:** Заявка с полной информацией или ошибка 404, если не найдена
        """
    )
    async def get_application(self, application_id: int, db_session: AsyncSession) -> ApplicationResponse:
        logger.info(f"GET /api/v1/applications/{application_id}")
        result = await db_session.execute(select(Application).where(Application.id == application_id))
        application = result.scalar_one_or_none()
        if not application:
            raise NotFoundException(detail=f"Заявка {application_id} не найдена")
        return ApplicationResponse.model_validate(application)
    
    @patch(
        "/{application_id:int}/status",
        summary="Изменить статус заявки",
        description="""
        Обновление статуса заявки.
        
        **Параметры пути:**
        - **application_id**: ID заявки (целое число)
        
        **Параметры запроса:**
        - **status**: Новый статус заявки (строка, например: "new", "in_progress", "completed", "rejected")
        
        **Требуется API ключ:** X-API-Key: internal-bot-key-2026
        
        **Пример:** PATCH /api/v1/applications/1/status?status=in_progress
        
        **Ответ:** Обновленная заявка
        """
    )
    async def update_status(self, application_id: int, db_session: AsyncSession, status: str = Parameter(query="status")) -> ApplicationResponse:
        logger.info(f"PATCH /api/v1/applications/{application_id}/status")
        result = await db_session.execute(select(Application).where(Application.id == application_id))
        application = result.scalar_one_or_none()
        if not application:
            raise NotFoundException(detail=f"Заявка {application_id} не найдена")
        application.status = status
        await db_session.commit()
        await db_session.refresh(application)
        return ApplicationResponse.model_validate(application)
    
    @delete(
        "/{application_id:int}",
        summary="Удалить заявку",
        description="""
        Удаление заявки из базы данных.
        
        **Параметры пути:**
        - **application_id**: ID заявки для удаления (целое число)
        
        **Требуется API ключ:** X-API-Key: internal-bot-key-2026
        
        **Ответ:** Сообщение об успешном удалении или ошибка 404, если заявка не найдена
        """,
        status_code=200
    )
    async def delete_application(self, application_id: int, db_session: AsyncSession) -> dict[str, str]:
        logger.info(f"DELETE /api/v1/applications/{application_id}")
        result = await db_session.execute(select(Application).where(Application.id == application_id))
        application = result.scalar_one_or_none()
        if not application:
            raise NotFoundException(detail=f"Заявка {application_id} не найдена")
        await db_session.delete(application)
        await db_session.commit()
        return {"message": "Заявка удалена"}
