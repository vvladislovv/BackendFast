"""Pydantic схемы для кейсов."""
from datetime import datetime
from pydantic import BaseModel, Field


class CaseBase(BaseModel):
    """Базовая схема кейса."""
    name: str = Field(..., min_length=1, max_length=255, description="Название кейса")
    about: str = Field(..., min_length=1, description="Краткое описание")
    tags: list[str] = Field(default_factory=list, description="Теги (Web, UI, React, TS)")
    image: str = Field(..., min_length=1, description="Путь к изображению")


class CaseCreate(CaseBase):
    """Схема создания кейса."""
    rating: int | None = Field(None, ge=0, description="Рейтинг для сортировки (по умолчанию 1)")


class CaseUpdate(BaseModel):
    """Схема обновления кейса."""
    name: str | None = Field(None, min_length=1, max_length=255)
    about: str | None = Field(None, min_length=1)
    tags: list[str] | None = None
    image: str | None = None


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
