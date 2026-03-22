"""Pydantic схемы для статей."""
from datetime import datetime
from pydantic import BaseModel, Field


class ArticleBase(BaseModel):
    """Базовая схема статьи."""
    title: str = Field(..., min_length=1, max_length=255, description="Название статьи")
    url: str = Field(..., min_length=1, description="Ссылка на статью")
    content: str = Field(..., min_length=1, description="Контент статьи в формате Markdown")
    photo: str | None = Field(None, description="Путь к фото")


class ArticleCreate(ArticleBase):
    """Схема создания статьи."""
    rating: int | None = Field(None, ge=0, description="Рейтинг для сортировки (по умолчанию 1)")


class ArticleUpdate(BaseModel):
    """Схема обновления статьи."""
    title: str | None = Field(None, min_length=1, max_length=255)
    url: str | None = Field(None, min_length=1)
    content: str | None = Field(None, min_length=1, description="Контент статьи в формате Markdown")
    photo: str | None = None


class ArticleResponse(ArticleBase):
    """Схема ответа со статьей."""
    id: int
    created_at: datetime
    updated_at: datetime
    is_hidden: bool
    rating: int
    
    class Config:
        from_attributes = True


class ArticleHideUpdate(BaseModel):
    """Схема для скрытия/показа статьи."""
    is_hidden: bool


class ArticleRatingUpdate(BaseModel):
    """Схема для изменения рейтинга."""
    rating: int = Field(..., ge=0)
