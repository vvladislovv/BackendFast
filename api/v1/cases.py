"""API endpoints для кейсов."""
from litestar import Controller, get, post, put, delete, patch
from litestar.di import Provide
from litestar.params import Dependency
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db_session
from schemas.case import (
    CaseCreate,
    CaseUpdate,
    CaseResponse,
    CaseHideUpdate,
    CaseRatingUpdate,
    CaseFreshUpdate,
)
from services.case_service import CaseService
from utils.logger import get_logger

logger = get_logger()


async def get_case_service(
    db_session: AsyncSession = Dependency(skip_validation=True),
) -> CaseService:
    """Dependency для получения сервиса кейсов."""
    return CaseService(db_session)


class CaseController(Controller):
    """Контроллер для работы с кейсами."""
    
    path = "/api/v1/cases"
    dependencies = {"case_service": Provide(get_case_service)}
    
    @post("/")
    async def create_case(
        self,
        data: CaseCreate,
        case_service: CaseService,
    ) -> CaseResponse:
        """Создать новый кейс."""
        logger.info("POST /api/v1/cases - создание кейса")
        case = await case_service.create(data)
        return CaseResponse.model_validate(case)
    
    @get("/")
    async def get_cases(
        self,
        case_service: CaseService,
        include_hidden: bool = False,
    ) -> list[CaseResponse]:
        """Получить все кейсы."""
        logger.info("GET /api/v1/cases - получение всех кейсов")
        cases = await case_service.get_all(include_hidden=include_hidden)
        return [CaseResponse.model_validate(c) for c in cases]
    
    @get("/fresh")
    async def get_fresh_cases(
        self,
        case_service: CaseService,
    ) -> list[CaseResponse]:
        """Получить свежие кейсы."""
        logger.info("GET /api/v1/cases/fresh - получение свежих кейсов")
        cases = await case_service.get_fresh()
        return [CaseResponse.model_validate(c) for c in cases]

    @get("/{case_id:int}")
    async def get_case(
        self,
        case_id: int,
        case_service: CaseService,
    ) -> CaseResponse:
        """Получить кейс по ID."""
        logger.info(f"GET /api/v1/cases/{case_id}")
        case = await case_service.get_by_id(case_id)
        return CaseResponse.model_validate(case)
    
    @put("/{case_id:int}")
    async def update_case(
        self,
        case_id: int,
        data: CaseUpdate,
        case_service: CaseService,
    ) -> CaseResponse:
        """Обновить кейс."""
        logger.info(f"PUT /api/v1/cases/{case_id}")
        case = await case_service.update(case_id, data)
        return CaseResponse.model_validate(case)
    
    @delete("/{case_id:int}")
    async def delete_case(
        self,
        case_id: int,
        case_service: CaseService,
    ) -> dict[str, str]:
        """Удалить кейс."""
        logger.info(f"DELETE /api/v1/cases/{case_id}")
        await case_service.delete(case_id)
        return {"message": "Кейс успешно удален"}
    
    @patch("/{case_id:int}/hide")
    async def toggle_case_hidden(
        self,
        case_id: int,
        data: CaseHideUpdate,
        case_service: CaseService,
    ) -> CaseResponse:
        """Скрыть/показать кейс."""
        logger.info(f"PATCH /api/v1/cases/{case_id}/hide")
        case = await case_service.toggle_hidden(case_id, data.is_hidden)
        return CaseResponse.model_validate(case)
    
    @patch("/{case_id:int}/rating")
    async def update_case_rating(
        self,
        case_id: int,
        data: CaseRatingUpdate,
        case_service: CaseService,
    ) -> CaseResponse:
        """Обновить рейтинг кейса."""
        logger.info(f"PATCH /api/v1/cases/{case_id}/rating")
        case = await case_service.update_rating(case_id, data.rating)
        return CaseResponse.model_validate(case)
    
    @patch("/{case_id:int}/fresh")
    async def toggle_case_fresh(
        self,
        case_id: int,
        data: CaseFreshUpdate,
        case_service: CaseService,
    ) -> CaseResponse:
        """Пометить кейс как свежий."""
        logger.info(f"PATCH /api/v1/cases/{case_id}/fresh")
        case = await case_service.toggle_fresh(case_id, data.is_fresh)
        return CaseResponse.model_validate(case)
