"""Pydantic схемы для статей."""
from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl


class ArticleBase(BaseModel):
    """Базовая схема статьи."""
    title: str = Field(..., min_length=1, max_length=255)
    url: HttpUrl
    photo_url: HttpUrl | None = None


class ArticleCreate(ArticleBase):
    """Схема создания статьи."""
    pass


class ArticleUpdate(BaseModel):
    """Схема обновления статьи."""
    title: str | None = Field(None, min_length=1, max_length=255)
    url: HttpUrl | None = None
    photo_url: HttpUrl | None = None


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
