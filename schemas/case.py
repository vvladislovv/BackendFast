"""Pydantic схемы для кейсов."""
from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl


class CaseBase(BaseModel):
    """Базовая схема кейса."""
    name: str = Field(..., min_length=1, max_length=255)
    about: str = Field(..., min_length=1)
    tags: list[str] = Field(default_factory=list)
    image_url: HttpUrl
    link_url: HttpUrl


class CaseCreate(CaseBase):
    """Схема создания кейса."""
    pass


class CaseUpdate(BaseModel):
    """Схема обновления кейса."""
    name: str | None = Field(None, min_length=1, max_length=255)
    about: str | None = Field(None, min_length=1)
    tags: list[str] | None = None
    image_url: HttpUrl | None = None
    link_url: HttpUrl | None = None


class CaseResponse(CaseBase):
    """Схема ответа с кейсом."""
    id: int
    created_at: datetime
    updated_at: datetime
    is_hidden: bool
    rating: int
    is_fresh: bool
    
    class Config:
        from_attributes = True


class CaseHideUpdate(BaseModel):
    """Схема для скрытия/показа кейса."""
    is_hidden: bool


class CaseRatingUpdate(BaseModel):
    """Схема для изменения рейтинга."""
    rating: int = Field(..., ge=0)


class CaseFreshUpdate(BaseModel):
    """Схема для пометки кейса как свежего."""
    is_fresh: bool
