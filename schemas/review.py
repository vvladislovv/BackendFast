"""Pydantic схемы для отзывов."""
from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl


class ReviewBase(BaseModel):
    """Базовая схема отзыва."""
    name: str = Field(..., min_length=1, max_length=255)
    company: str = Field(..., min_length=1, max_length=255)
    review_text: str = Field(..., min_length=1)
    stars: int = Field(..., ge=1, le=5)
    photo_url: HttpUrl | None = None


class ReviewCreate(ReviewBase):
    """Схема создания отзыва."""
    pass


class ReviewUpdate(BaseModel):
    """Схема обновления отзыва."""
    name: str | None = Field(None, min_length=1, max_length=255)
    company: str | None = Field(None, min_length=1, max_length=255)
    review_text: str | None = Field(None, min_length=1)
    stars: int | None = Field(None, ge=1, le=5)
    photo_url: HttpUrl | None = None


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
