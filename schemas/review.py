"""Pydantic схемы для отзывов."""
from datetime import datetime
from pydantic import BaseModel, Field


class ReviewBase(BaseModel):
    """Базовая схема отзыва."""
    name: str = Field(..., min_length=1, max_length=255, description="Имя автора отзыва")
    company: str = Field(..., min_length=1, max_length=255, description="Компания")
    review: str = Field(..., min_length=1, description="Текст отзыва")
    stars: int = Field(..., ge=1, le=5, description="Количество звезд (1-5)")
    photo: str | None = Field(None, description="Путь к фото")


class ReviewCreate(ReviewBase):
    """Схема создания отзыва."""
    rating: int | None = Field(None, ge=1, description="Рейтинг для сортировки (по умолчанию 1)")


class ReviewUpdate(BaseModel):
    """Схема обновления отзыва."""
    name: str | None = Field(None, min_length=1, max_length=255)
    company: str | None = Field(None, min_length=1, max_length=255)
    review: str | None = Field(None, min_length=1)
    stars: int | None = Field(None, ge=1, le=5)
    photo: str | None = None


class ReviewResponse(ReviewBase):
    """Схема ответа с отзывом."""
    id: int
    created_at: datetime
    updated_at: datetime
    is_hidden: bool
    rating: int
    
    class Config:
        from_attributes = True


class ReviewHideUpdate(BaseModel):
    """Схема для скрытия/показа отзыва."""
    is_hidden: bool


class ReviewRatingUpdate(BaseModel):
    """Схема для изменения рейтинга."""
    rating: int = Field(..., ge=0)
