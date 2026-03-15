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
        Создание новой вакансии.
        
        **Параметры тела запроса (JSON):**
        - **title** (обязательно): Название вакансии (1-255 символов)
        - **description** (обязательно): Описание вакансии (минимум 1 символ)
        - **requirements** (опционально): Требования к кандидату
        - **salary_from** (опционально): Зарплата от (целое число)
        - **salary_to** (опционально): Зарплата до (целое число)
        - **location** (опционально): Местоположение (до 255 символов)
        - **employment_type** (опционально): Тип занятости (до 100 символов, например: "Полная занятость", "Удаленная работа")
        - **experience** (опционально): Требуемый опыт (до 100 символов, например: "1-3 года", "Без опыта")
        
        **Требуется API ключ:** X-API-Key: internal-bot-key-2026
        
        **Ответ:** Созданная вакансия с рейтингом 0 и статусом is_hidden=false
        """,
        status_code=201
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
        Получение всех видимых вакансий (is_hidden=false), отсортированных по рейтингу.
        
        **Параметры query:**
        - **include_hidden** (опционально): true - включить скрытые вакансии, false - только видимые (по умолчанию)
        
        **Требуется API ключ:** X-API-Key: internal-bot-key-2026
        
        **Ответ:** Массив вакансий
        """
    )
    async def get_vacancies(self, vacancy_service: VacancyService = Dependency(), include_hidden: bool = Parameter(default=False, query="include_hidden")) -> list[VacancyResponse]:
        """Получить все вакансии."""
        logger.info(f"GET /api/v1/vacancies?include_hidden={include_hidden}")
        vacancies = await vacancy_service.get_all(include_hidden=include_hidden)
        return [VacancyResponse.model_validate(v) for v in vacancies]
    
    @get(
        "/{vacancy_id:int}",
        summary="Получить вакансию по ID",
        description="""
        Получение конкретной вакансии по её ID.
        
        **Параметры пути:**
        - **vacancy_id**: ID вакансии (целое число)
        
        **Требуется API ключ:** X-API-Key: internal-bot-key-2026
        
        **Ответ:** Вакансия с полной информацией или ошибка 404
        """
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
        Полное обновление вакансии.
        
        **Параметры пути:**
        - **vacancy_id**: ID вакансии (целое число)
        
        **Параметры тела запроса (JSON):** Все поля опциональны
        - **title**: Новое название вакансии
        - **description**: Новое описание
        - **requirements**: Новые требования
        - **salary_from**: Новая зарплата от
        - **salary_to**: Новая зарплата до
        - **location**: Новое местоположение
        - **employment_type**: Новый тип занятости
        - **experience**: Новый требуемый опыт
        
        **Требуется API ключ:** X-API-Key: internal-bot-key-2026
        
        **Ответ:** Обновленная вакансия
        """
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
        Удаление вакансии из базы данных.
        
        **Параметры пути:**
        - **vacancy_id**: ID вакансии (целое число)
        
        **Требуется API ключ:** X-API-Key: internal-bot-key-2026
        
        **Ответ:** Сообщение об успешном удалении
        """,
        status_code=200
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
        Изменение видимости вакансии.
        
        **Параметры пути:**
        - **vacancy_id**: ID вакансии (целое число)
        
        **Параметры тела запроса (JSON):**
        - **is_hidden** (обязательно): true - скрыть вакансию, false - показать вакансию
        
        **Требуется API ключ:** X-API-Key: internal-bot-key-2026
        
        **Ответ:** Обновленная вакансия
        """
    )
    async def toggle_vacancy_hidden(
        self,
        vacancy_id: int,
        data: VacancyHideUpdate,
        vacancy_service: VacancyService,
    ) -> VacancyResponse:
        """Скрыть/показать вакансию."""
        logger.info(f"PATCH /api/v1/vacancies/{vacancy_id}/hide")
        vacancy = await vacancy_service.toggle_hidden(vacancy_id, data.is_hidden)
        return VacancyResponse.model_validate(vacancy)
    
    @patch(
        "/{vacancy_id:int}/rating",
        summary="Обновить рейтинг вакансии",
        description="""
        Изменение рейтинга вакансии для сортировки.
        
        **Параметры пути:**
        - **vacancy_id**: ID вакансии (целое число)
        
        **Параметры query:**
        - **rating** (обязательно): Новый рейтинг (целое число >= 0)
        
        **Требуется API ключ:** X-API-Key: internal-bot-key-2026
        
        **Пример:** PATCH /api/v1/vacancies/5/rating?rating=100
        
        **Ответ:** Обновленная вакансия
        """
    )
    async def update_vacancy_rating(
        self,
        vacancy_id: int,
        rating: int = Parameter(ge=0, query="rating", description="Новый рейтинг (>= 0)"),
        vacancy_service: VacancyService = Dependency(),
    ) -> VacancyResponse:
        """Обновить рейтинг вакансии."""
        logger.info(f"PATCH /api/v1/vacancies/{vacancy_id}/rating?rating={rating}")
        vacancy = await vacancy_service.update_rating(vacancy_id, rating)
        return VacancyResponse.model_validate(vacancy)
