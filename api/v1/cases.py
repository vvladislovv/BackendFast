"""API endpoints для кейсов."""
from litestar import Controller, get, post, put, delete, patch
from litestar.di import Provide
from litestar.params import Dependency, Parameter
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db_session
from schemas.case import CaseCreate, CaseUpdate, CaseResponse, CaseHideUpdate, CaseFreshUpdate
from services.case_service import CaseService
from utils.logger import get_logger

logger = get_logger()


async def get_case_service(db_session: AsyncSession = Dependency(skip_validation=True)) -> CaseService:
    return CaseService(db_session)


class CaseController(Controller):
    path = "/api/v1/cases"
    tags = ["Cases"]
    dependencies = {"case_service": Provide(get_case_service)}

    @post("/", summary="Создать кейс", description="Создание нового кейса. **Параметры (JSON):** title (обязательно, 1-255 символов), description (обязательно), client (опционально, до 255 символов), technologies (опционально). **Требуется API ключ**", status_code=201)
    async def create_case(self, data: CaseCreate, case_service: CaseService) -> CaseResponse:
        logger.info("POST /api/v1/cases")
        case = await case_service.create(data)
        return CaseResponse.model_validate(case)

    @get("/", summary="Получить список кейсов", description="Получение всех видимых кейсов (is_hidden=false). **Требуется API ключ**")
    async def get_cases(self, case_service: CaseService) -> list[CaseResponse]:
        logger.info("GET /api/v1/cases")
        cases = await case_service.get_all(include_hidden=False)
        return [CaseResponse.model_validate(c) for c in cases]

    @get("/fresh", summary="Получить свежие кейсы", description="Получение кейсов с флагом is_fresh=true. **Требуется API ключ**")
    async def get_fresh_cases(self, case_service: CaseService) -> list[CaseResponse]:
        logger.info("GET /api/v1/cases/fresh")
        cases = await case_service.get_fresh()
        return [CaseResponse.model_validate(c) for c in cases]

    @get("/{case_id:int}", summary="Получить кейс", description="Получение кейса по ID. **Параметр пути:** case_id. **Требуется API ключ**")
    async def get_case(self, case_id: int, case_service: CaseService) -> CaseResponse:
        logger.info(f"GET /api/v1/cases/{case_id}")
        case = await case_service.get_by_id(case_id)
        return CaseResponse.model_validate(case)

    @put("/{case_id:int}", summary="Обновить кейс", description="Обновление кейса. **Параметр пути:** case_id. **Параметры (JSON):** title, description, client, technologies (все опциональны). **Требуется API ключ**")
    async def update_case(self, case_id: int, data: CaseUpdate, case_service: CaseService) -> CaseResponse:
        logger.info(f"PUT /api/v1/cases/{case_id}")
        case = await case_service.update(case_id, data)
        return CaseResponse.model_validate(case)

    @delete("/{case_id:int}", summary="Удалить кейс", description="Удаление кейса. **Параметр пути:** case_id. **Требуется API ключ**", status_code=200)
    async def delete_case(self, case_id: int, case_service: CaseService) -> dict[str, str]:
        logger.info(f"DELETE /api/v1/cases/{case_id}")
        await case_service.delete(case_id)
        return {"message": "Кейс удален"}

    @patch("/{case_id:int}/hide", summary="Скрыть/показать кейс", description="Изменение видимости. **Параметр пути:** case_id. **Параметр (JSON):** is_hidden (true/false). **Требуется API ключ**")
    async def toggle_case_hidden(self, case_id: int, data: CaseHideUpdate, case_service: CaseService) -> CaseResponse:
        logger.info(f"PATCH /api/v1/cases/{case_id}/hide")
        case = await case_service.toggle_hidden(case_id, data.is_hidden)
        return CaseResponse.model_validate(case)

    @patch("/{case_id:int}/rating", summary="Обновить рейтинг", description="Изменение рейтинга кейса. **Параметр пути:** case_id. **Параметр query:** rating (целое число >= 0). **Пример:** PATCH /api/v1/cases/5/rating?rating=100. **Требуется API ключ**")
    async def update_case_rating(self, case_id: int, rating: int = Parameter(ge=0, query="rating"), case_service: CaseService = Dependency()) -> CaseResponse:
        logger.info(f"PATCH /api/v1/cases/{case_id}/rating?rating={rating}")
        case = await case_service.update_rating(case_id, rating)
        return CaseResponse.model_validate(case)

    @patch("/{case_id:int}/fresh", summary="Пометить как свежий", description="Изменение флага свежести. **Параметр пути:** case_id. **Параметр (JSON):** is_fresh (true/false). **Требуется API ключ**")
    async def toggle_case_fresh(self, case_id: int, data: CaseFreshUpdate, case_service: CaseService) -> CaseResponse:
        logger.info(f"PATCH /api/v1/cases/{case_id}/fresh")
        case = await case_service.toggle_fresh(case_id, data.is_fresh)
        return CaseResponse.model_validate(case)
