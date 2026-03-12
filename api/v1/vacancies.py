"""API endpoints для вакансий."""
from litestar import Controller, get, post, put, delete, patch
from litestar.di import Provide
from litestar.params import Dependency
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
    dependencies = {"vacancy_service": Provide(get_vacancy_service)}
    
    @post("/")
    async def create_vacancy(
        self,
        data: VacancyCreate,
        vacancy_service: VacancyService,
    ) -> VacancyResponse:
        """Создать новую вакансию."""
        logger.info("POST /api/v1/vacancies - создание вакансии")
        vacancy = await vacancy_service.create(data)
        return VacancyResponse.model_validate(vacancy)
    
    @get("/")
    async def get_vacancies(
        self,
        vacancy_service: VacancyService,
        include_hidden: bool = False,
    ) -> list[VacancyResponse]:
        """Получить все вакансии."""
        logger.info("GET /api/v1/vacancies - получение всех вакансий")
        vacancies = await vacancy_service.get_all(include_hidden=include_hidden)
        return [VacancyResponse.model_validate(v) for v in vacancies]
    
    @get("/{vacancy_id:int}")
    async def get_vacancy(
        self,
        vacancy_id: int,
        vacancy_service: VacancyService,
    ) -> VacancyResponse:
        """Получить вакансию по ID."""
        logger.info(f"GET /api/v1/vacancies/{vacancy_id}")
        vacancy = await vacancy_service.get_by_id(vacancy_id)
        return VacancyResponse.model_validate(vacancy)

    @put("/{vacancy_id:int}")
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
    
    @delete("/{vacancy_id:int}")
    async def delete_vacancy(
        self,
        vacancy_id: int,
        vacancy_service: VacancyService,
    ) -> dict[str, str]:
        """Удалить вакансию."""
        logger.info(f"DELETE /api/v1/vacancies/{vacancy_id}")
        await vacancy_service.delete(vacancy_id)
        return {"message": "Вакансия успешно удалена"}
    
    @patch("/{vacancy_id:int}/hide")
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
    
    @patch("/{vacancy_id:int}/rating")
    async def update_vacancy_rating(
        self,
        vacancy_id: int,
        data: VacancyRatingUpdate,
        vacancy_service: VacancyService,
    ) -> VacancyResponse:
        """Обновить рейтинг вакансии."""
        logger.info(f"PATCH /api/v1/vacancies/{vacancy_id}/rating")
        vacancy = await vacancy_service.update_rating(vacancy_id, data.rating)
        return VacancyResponse.model_validate(vacancy)
