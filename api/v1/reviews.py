"""API endpoints для отзывов."""
from litestar import Controller, get, post, put, delete, patch
from litestar.di import Provide
from litestar.params import Dependency
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db_session
from schemas.review import (
    ReviewCreate,
    ReviewUpdate,
    ReviewResponse,
    ReviewHideUpdate,
    ReviewRatingUpdate,
)
from services.review_service import ReviewService
from utils.logger import get_logger

logger = get_logger()


async def get_review_service(
    db_session: AsyncSession = Dependency(skip_validation=True),
) -> ReviewService:
    """Dependency для получения сервиса отзывов."""
    return ReviewService(db_session)


class ReviewController(Controller):
    """Контроллер для работы с отзывами."""
    
    path = "/api/v1/reviews"
    dependencies = {"review_service": Provide(get_review_service)}
    
    @post("/")
    async def create_review(
        self,
        data: ReviewCreate,
        review_service: ReviewService,
    ) -> ReviewResponse:
        """Создать новый отзыв."""
        logger.info("POST /api/v1/reviews - создание отзыва")
        review = await review_service.create(data)
        return ReviewResponse.model_validate(review)
    
    @get("/")
    async def get_reviews(
        self,
        review_service: ReviewService,
        include_hidden: bool = False,
    ) -> list[ReviewResponse]:
        """Получить все отзывы."""
        logger.info("GET /api/v1/reviews - получение всех отзывов")
        reviews = await review_service.get_all(include_hidden=include_hidden)
        return [ReviewResponse.model_validate(r) for r in reviews]
    
    @get("/{review_id:int}")
    async def get_review(
        self,
        review_id: int,
        review_service: ReviewService,
    ) -> ReviewResponse:
        """Получить отзыв по ID."""
        logger.info(f"GET /api/v1/reviews/{review_id}")
        review = await review_service.get_by_id(review_id)
        return ReviewResponse.model_validate(review)

    @put("/{review_id:int}")
    async def update_review(
        self,
        review_id: int,
        data: ReviewUpdate,
        review_service: ReviewService,
    ) -> ReviewResponse:
        """Обновить отзыв."""
        logger.info(f"PUT /api/v1/reviews/{review_id}")
        review = await review_service.update(review_id, data)
        return ReviewResponse.model_validate(review)
    
    @delete("/{review_id:int}")
    async def delete_review(
        self,
        review_id: int,
        review_service: ReviewService,
    ) -> dict[str, str]:
        """Удалить отзыв."""
        logger.info(f"DELETE /api/v1/reviews/{review_id}")
        await review_service.delete(review_id)
        return {"message": "Отзыв успешно удален"}
    
    @patch("/{review_id:int}/hide")
    async def toggle_review_hidden(
        self,
        review_id: int,
        data: ReviewHideUpdate,
        review_service: ReviewService,
    ) -> ReviewResponse:
        """Скрыть/показать отзыв."""
        logger.info(f"PATCH /api/v1/reviews/{review_id}/hide")
        review = await review_service.toggle_hidden(review_id, data.is_hidden)
        return ReviewResponse.model_validate(review)
    
    @patch("/{review_id:int}/rating")
    async def update_review_rating(
        self,
        review_id: int,
        data: ReviewRatingUpdate,
        review_service: ReviewService,
    ) -> ReviewResponse:
        """Обновить рейтинг отзыва."""
        logger.info(f"PATCH /api/v1/reviews/{review_id}/rating")
        review = await review_service.update_rating(review_id, data.rating)
        return ReviewResponse.model_validate(review)
