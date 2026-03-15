"""API endpoints для отзывов."""
from litestar import Controller, get, post, put, delete, patch
from litestar.di import Provide
from litestar.params import Dependency, Parameter
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db_session
from schemas.review import ReviewCreate, ReviewUpdate, ReviewResponse, ReviewHideUpdate
from services.review_service import ReviewService
from utils.logger import get_logger

logger = get_logger()


async def get_review_service(db_session: AsyncSession = Dependency(skip_validation=True)) -> ReviewService:
    return ReviewService(db_session)


class ReviewController(Controller):
    path = "/api/v1/reviews"
    tags = ["Reviews"]
    dependencies = {"review_service": Provide(get_review_service)}

    @post("/", summary="Создать отзыв", description="Создание нового отзыва. **Параметры (JSON):** author (обязательно, 1-255 символов), content (обязательно), rating (опционально, целое число). **Требуется API ключ**", status_code=201)
    async def create_review(self, data: ReviewCreate, review_service: ReviewService) -> ReviewResponse:
        logger.info("POST /api/v1/reviews")
        review = await review_service.create(data)
        return ReviewResponse.model_validate(review)

    @get("/", summary="Получить список отзывов", description="Получение всех видимых отзывов (is_hidden=false). **Требуется API ключ**")
    async def get_reviews(self, review_service: ReviewService) -> list[ReviewResponse]:
        logger.info("GET /api/v1/reviews")
        reviews = await review_service.get_all(include_hidden=False)
        return [ReviewResponse.model_validate(r) for r in reviews]

    @get("/{review_id:int}", summary="Получить отзыв", description="Получение отзыва по ID. **Параметр пути:** review_id (целое число). **Требуется API ключ**")
    async def get_review(self, review_id: int, review_service: ReviewService) -> ReviewResponse:
        logger.info(f"GET /api/v1/reviews/{review_id}")
        review = await review_service.get_by_id(review_id)
        return ReviewResponse.model_validate(review)

    @put("/{review_id:int}", summary="Обновить отзыв", description="Обновление отзыва. **Параметр пути:** review_id. **Параметры (JSON):** author, content, rating (все опциональны). **Требуется API ключ**")
    async def update_review(self, review_id: int, data: ReviewUpdate, review_service: ReviewService) -> ReviewResponse:
        logger.info(f"PUT /api/v1/reviews/{review_id}")
        review = await review_service.update(review_id, data)
        return ReviewResponse.model_validate(review)

    @delete("/{review_id:int}", summary="Удалить отзыв", description="Удаление отзыва. **Параметр пути:** review_id. **Требуется API ключ**", status_code=200)
    async def delete_review(self, review_id: int, review_service: ReviewService) -> dict[str, str]:
        logger.info(f"DELETE /api/v1/reviews/{review_id}")
        await review_service.delete(review_id)
        return {"message": "Отзыв удален"}

    @patch("/{review_id:int}/hide", summary="Скрыть/показать отзыв", description="Изменение видимости. **Параметр пути:** review_id. **Параметр (JSON):** is_hidden (true/false). **Требуется API ключ**")
    async def toggle_review_hidden(self, review_id: int, data: ReviewHideUpdate, review_service: ReviewService) -> ReviewResponse:
        logger.info(f"PATCH /api/v1/reviews/{review_id}/hide")
        review = await review_service.toggle_hidden(review_id, data.is_hidden)
        return ReviewResponse.model_validate(review)

    @patch("/{review_id:int}/rating", summary="Обновить рейтинг", description="Изменение рейтинга отзыва. **Параметр пути:** review_id. **Параметр query:** rating (целое число >= 0). **Пример:** PATCH /api/v1/reviews/5/rating?rating=100. **Требуется API ключ**")
    async def update_review_rating(self, review_id: int, rating: int = Parameter(ge=0, query="rating"), review_service: ReviewService = Dependency()) -> ReviewResponse:
        logger.info(f"PATCH /api/v1/reviews/{review_id}/rating?rating={rating}")
        review = await review_service.update_rating(review_id, rating)
        return ReviewResponse.model_validate(review)
