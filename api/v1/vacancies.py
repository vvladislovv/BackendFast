"""API endpoints для вакансий."""
from litestar import Controller, get, post, put, delete, patch
from litestar.di import Provide
from litestar.params import Dependency, Parameter
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db_session
from schemas.vacancy import (
    VacancyCreate,
    VacancyUpdate,
    VacancyResponse,
    VacancyHideUpdate,
    VacancyRatingUpdate,
)
from services.vacancy_service import VacancyService
from utils.logger import get_logger

logger = get_logger()


async def get_vacancy_service(
    db_session: AsyncSession = Dependency(skip_validation=True),
) -> VacancyService:
    """Dependency для получения сервиса вакансий."""
    return VacancyService(db_session)


class VacancyController(Controller):
    """Контроллер для работы с вакансиями."""
    
    path = "/api/v1/vacancies"
    tags = ["Vacancies"]
    dependencies = {"vacancy_service": Provide(get_vacancy_service)}
    
    @post(
        "/",
        summary="Создать вакансию",
        description="""
        Создает новую вакансию в системе.
        
        **Обязательные поля:**
        - `title` - Название вакансии (1-255 символов)
        - `url` - Ссылка на вакансию (1-500 символов, валидный URL)
        - `employment_type` - Тип занятости (1-100 символов)
        
        **Опциональные поля:**
        - `description` - Описание вакансии
        
        **Возможные ошибки:**
        - `400` - Ошибка валидации (неверный формат данных, пустые обязательные поля)
        - `500` - Внутренняя ошибка сервера
        """,
        status_code=201,
    )
    async def create_vacancy(
        self,
        data: VacancyCreate,
        vacancy_service: VacancyService,
    ) -> VacancyResponse:
        """Создать новую вакансию."""
        logger.info("POST /api/v1/vacancies - создание вакансии")
        vacancy = await vacancy_service.create(data)
        return VacancyResponse.model_validate(vacancy)
    
    @get(
        "/",
        summary="Получить список вакансий",
        description="""
        Возвращает список всех вакансий.
        
        **Query параметры:**
        - `include_hidden` (bool, default=false) - Включить скрытые вакансии
        
        **Ответ:**
        - `200` - Массив вакансий (может быть пустым)
        
        **Сортировка:** По рейтингу (DESC), затем по дате создания (DESC)
        """,
    )
    async def get_vacancies(
        self,
        vacancy_service: VacancyService,
        include_hidden: bool = False,
    ) -> list[VacancyResponse]:
        """Получить все вакансии."""
        logger.info("GET /api/v1/vacancies - получение всех вакансий")
        vacancies = await vacancy_service.get_all(include_hidden=include_hidden)
        return [VacancyResponse.model_validate(v) for v in vacancies]
    
    @get(
        "/{vacancy_id:int}",
        summary="Получить вакансию по ID",
        description="""
        Возвращает одну вакансию по её ID.
        
        **Path параметры:**
        - `vacancy_id` (int) - ID вакансии
        
        **Возможные ответы:**
        - `200` - Вакансия найдена
        - `404` - Вакансия не найдена
        """,
    )
    async def get_vacancy(
        self,
        vacancy_id: int,
        vacancy_service: VacancyService,
    ) -> VacancyResponse:
        """Получить вакансию по ID."""
        logger.info(f"GET /api/v1/vacancies/{vacancy_id}")
        vacancy = await vacancy_service.get_by_id(vacancy_id)
        return VacancyResponse.model_validate(vacancy)

    @put(
        "/{vacancy_id:int}",
        summary="Обновить вакансию",
        description="""
        Обновляет существующую вакансию. Все поля опциональны.
        
        **Path параметры:**
        - `vacancy_id` (int) - ID вакансии
        
        **Поля для обновления:**
        - `title` - Новое название (1-255 символов)
        - `url` - Новая ссылка (1-500 символов)
        - `employment_type` - Новый тип занятости (1-100 символов)
        - `description` - Новое описание
        
        **Возможные ответы:**
        - `200` - Вакансия обновлена
        - `400` - Ошибка валидации
        - `404` - Вакансия не найдена
        """,
    )
    async def update_vacancy(
        self,
        vacancy_id: int,
        data: VacancyUpdate,
        vacancy_service: VacancyService,
    ) -> VacancyResponse:
        """Обновить вакансию."""
        logger.info(f"PUT /api/v1/vacancies/{vacancy_id}")
        vacancy = await vacancy_service.update(vacancy_id, data)
        return VacancyResponse.model_validate(vacancy)
    
    @delete(
        "/{vacancy_id:int}",
        summary="Удалить вакансию",
        description="""
        Удаляет вакансию из системы безвозвратно.
        
        **Path параметры:**
        - `vacancy_id` (int) - ID вакансии
        
        **Возможные ответы:**
        - `200` - Вакансия удалена
        - `404` - Вакансия не найдена
        """,
        status_code=200,
    )
    async def delete_vacancy(
        self,
        vacancy_id: int,
        vacancy_service: VacancyService,
    ) -> dict[str, str]:
        """Удалить вакансию."""
        logger.info(f"DELETE /api/v1/vacancies/{vacancy_id}")
        await vacancy_service.delete(vacancy_id)
        return {"message": "Вакансия успешно удалена"}
    
    @patch(
        "/{vacancy_id:int}/hide",
        summary="Скрыть/показать вакансию",
        description="""
        Изменяет видимость вакансии без удаления.
        
        **Path параметры:**
        - `vacancy_id` (int) - ID вакансии
        
        **Query параметры:**
        - `is_hidden` (bool, optional) - true для скрытия, false для показа. Если не указан, переключает текущее состояние
        
        **Возможные ответы:**
        - `200` - Видимость изменена
        - `404` - Вакансия не найдена
        """,
    )
    async def toggle_vacancy_hidden(
        self,
        vacancy_id: int,
        vacancy_service: VacancyService,
        is_hidden: bool | None = Parameter(default=None, query="is_hidden"),
    ) -> VacancyResponse:
        """Скрыть/показать вакансию."""
        logger.info(f"PATCH /api/v1/vacancies/{vacancy_id}/hide")
        
        # Если is_hidden не указан, переключаем текущее состояние
        if is_hidden is None:
            vacancy = await vacancy_service.get_by_id(vacancy_id)
            is_hidden = not vacancy.is_hidden
        
        vacancy = await vacancy_service.toggle_hidden(vacancy_id, is_hidden)
        return VacancyResponse.model_validate(vacancy)
    
    @patch(
        "/{vacancy_id:int}/rating",
        summary="Обновить рейтинг вакансии",
        description="""
        Изменяет рейтинг вакансии для сортировки.
        
        **Path параметры:**
        - `vacancy_id` (int) - ID вакансии
        
        **Query параметры:**
        - `rating` (int, >= 0) - Новый рейтинг
        
        **Возможные ответы:**
        - `200` - Рейтинг обновлен
        - `400` - Некорректное значение рейтинга
        - `404` - Вакансия не найдена
        """,
    )
    async def update_vacancy_rating(
        self,
        vacancy_id: int,
        vacancy_service: VacancyService,
        rating: int = Parameter(default=1, query="rating"),
    ) -> VacancyResponse:
        """Обновить рейтинг вакансии."""
        logger.info(f"PATCH /api/v1/vacancies/{vacancy_id}/rating")
        vacancy = await vacancy_service.update_rating(vacancy_id, rating)
        return VacancyResponse.model_validate(vacancy)
