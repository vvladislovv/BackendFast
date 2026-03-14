"""Сервис для работы с отзывами."""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.review import Review
from schemas.review import ReviewCreate, ReviewUpdate
from utils.exceptions import NotFoundException
from utils.logger import get_logger

logger = get_logger()


class ReviewService:
    """Сервис для CRUD операций с отзывами."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, data: ReviewCreate) -> Review:
        """Создать отзыв."""
        logger.info(f"Создание отзыва от: {data.name}")
        
        review_data = {k: v for k, v in data.model_dump(exclude_none=False).items() if v is not None}
        review = Review(**review_data)
        self.session.add(review)
        await self.session.commit()
        await self.session.refresh(review)
        
        logger.info(f"Отзыв создан с ID: {review.id}")
        return review
    
    async def get_all(self, include_hidden: bool = False) -> list[Review]:
        """Получить все отзывы."""
        logger.info("Получение всех отзывов")
        
        query = select(Review).order_by(Review.rating.desc(), Review.created_at.desc())
        
        if not include_hidden:
            query = query.where(Review.is_hidden == False)
        
        result = await self.session.execute(query)
        reviews = result.scalars().all()
        
        logger.info(f"Найдено отзывов: {len(reviews)}")
        return list(reviews)

    async def get_by_id(self, review_id: int) -> Review:
        """Получить отзыв по ID."""
        logger.info(f"Получение отзыва с ID: {review_id}")
        
        result = await self.session.execute(
            select(Review).where(Review.id == review_id)
        )
        review = result.scalar_one_or_none()
        
        if not review:
            logger.error("Отзыв с ID {} не найден", review_id)
            raise NotFoundException(f"Отзыв с ID {review_id} не найден")
        
        return review
    
    async def update(self, review_id: int, data: ReviewUpdate) -> Review:
        """Обновить отзыв."""
        logger.info(f"Обновление отзыва с ID: {review_id}")
        
        review = await self.get_by_id(review_id)
        
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(review, field, value)
        
        await self.session.commit()
        await self.session.refresh(review)
        
        logger.info(f"Отзыв {review_id} обновлен")
        return review
    
    async def delete(self, review_id: int) -> None:
        """Удалить отзыв."""
        logger.info(f"Удаление отзыва с ID: {review_id}")
        
        review = await self.get_by_id(review_id)
        await self.session.delete(review)
        await self.session.commit()
        
        logger.info(f"Отзыв {review_id} удален")
    
    async def toggle_hidden(self, review_id: int, is_hidden: bool) -> Review:
        """Скрыть/показать отзыв."""
        logger.info(f"Изменение видимости отзыва {review_id}: is_hidden={is_hidden}")
        
        review = await self.get_by_id(review_id)
        review.is_hidden = is_hidden
        
        await self.session.commit()
        await self.session.refresh(review)
        
        logger.info(f"Видимость отзыва {review_id} изменена")
        return review
    
    async def update_rating(self, review_id: int, rating: int) -> Review:
        """Обновить рейтинг отзыва."""
        logger.info(f"Обновление рейтинга отзыва {review_id}: rating={rating}")
        
        review = await self.get_by_id(review_id)
        review.rating = rating
        
        await self.session.commit()
        await self.session.refresh(review)
        
        logger.info(f"Рейтинг отзыва {review_id} обновлен")
        return review
