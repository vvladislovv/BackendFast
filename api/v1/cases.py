"""API endpoints для кейсов."""
from litestar import Controller, get, post, put, delete, patch
from litestar.di import Provide
from litestar.params import Dependency, Parameter
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
    tags = ["Cases"]
    dependencies = {"case_service": Provide(get_case_service)}

    @post(
        "/",
        summary="Создать кейс",
        description="Создает новый кейс проекта с тегами",
        status_code=201,
    )
    async def create_case(
        self,
        data: CaseCreate,
        case_service: CaseService,
    ) -> CaseResponse:
        """Создать новый кейс."""
        logger.info("POST /api/v1/cases - создание кейса")
        case = await case_service.create(data)
        return CaseResponse.model_validate(case)

    @get(
        "/",
        summary="Получить список кейсов",
        description="Возвращает список всех кейсов, отсортированных по рейтингу",
    )
    async def get_cases(
        self,
        case_service: CaseService,
        include_hidden: bool = False,
    ) -> list[CaseResponse]:
        """Получить все кейсы."""
        logger.info("GET /api/v1/cases - получение всех кейсов")
        cases = await case_service.get_all(include_hidden=include_hidden)
        return [CaseResponse.model_validate(c) for c in cases]

    @get(
        "/fresh",
        summary="Получить свежие кейсы",
        description="Возвращает только кейсы, помеченные как свежие",
    )
    async def get_fresh_cases(
        self,
        case_service: CaseService,
    ) -> list[CaseResponse]:
        """Получить свежие кейсы."""
        logger.info("GET /api/v1/cases/fresh - получение свежих кейсов")
        cases = await case_service.get_fresh()
        return [CaseResponse.model_validate(c) for c in cases]

    @get(
        "/{case_id:int}",
        summary="Получить кейс по ID",
        description="Возвращает один кейс по его ID",
    )
    async def get_case(
        self,
        case_id: int,
        case_service: CaseService,
    ) -> CaseResponse:
        """Получить кейс по ID."""
        logger.info(f"GET /api/v1/cases/{case_id}")
        case = await case_service.get_by_id(case_id)
        return CaseResponse.model_validate(case)

    @put(
        "/{case_id:int}",
        summary="Обновить кейс",
        description="Обновляет существующий кейс. Все поля опциональны",
    )
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

    @delete(
        "/{case_id:int}",
        summary="Удалить кейс",
        description="Удаляет кейс из системы безвозвратно",
        status_code=200,
    )
    async def delete_case(
        self,
        case_id: int,
        case_service: CaseService,
    ) -> dict[str, str]:
        """Удалить кейс."""
        logger.info(f"DELETE /api/v1/cases/{case_id}")
        await case_service.delete(case_id)
        return {"message": "Кейс успешно удален"}

    @patch(
        "/{case_id:int}/hide",
        summary="Скрыть/показать кейс",
        description="Изменяет видимость кейса без удаления",
    )
    async def toggle_case_hidden(
        self,
        case_id: int,
        case_service: CaseService,
        is_hidden: bool | None = Parameter(default=None, query="is_hidden"),
    ) -> CaseResponse:
        """Скрыть/показать кейс."""
        logger.info(f"PATCH /api/v1/cases/{case_id}/hide")
        
        if is_hidden is None:
            case = await case_service.get_by_id(case_id)
            is_hidden = not case.is_hidden
        
        case = await case_service.toggle_hidden(case_id, is_hidden)
        return CaseResponse.model_validate(case)

    @patch(
        "/{case_id:int}/rating",
        summary="Обновить рейтинг кейса",
        description="Изменяет рейтинг кейса для сортировки",
    )
    async def update_case_rating(
        self,
        case_id: int,
        case_service: CaseService,
        rating: int = Parameter(default=1, query="rating"),
    ) -> CaseResponse:
        """Обновить рейтинг кейса."""
        logger.info(f"PATCH /api/v1/cases/{case_id}/rating")
        case = await case_service.update_rating(case_id, rating)
        return CaseResponse.model_validate(case)

    @patch(
        "/{case_id:int}/fresh",
        summary="Пометить кейс как свежий",
        description="Изменяет статус 'свежести' кейса",
    )
    async def toggle_case_fresh(
        self,
        case_id: int,
        case_service: CaseService,
        is_fresh: bool | None = Parameter(default=None, query="is_fresh"),
    ) -> CaseResponse:
        """Пометить кейс как свежий."""
        logger.info(f"PATCH /api/v1/cases/{case_id}/fresh")
        
        if is_fresh is None:
            case = await case_service.get_by_id(case_id)
            is_fresh = not case.is_fresh
        
        case = await case_service.toggle_fresh(case_id, is_fresh)
        return CaseResponse.model_validate(case)

