"""Pydantic схемы для вакансий."""
from datetime import datetime
from pydantic import BaseModel, Field


class VacancyBase(BaseModel):
    """Базовая схема вакансии."""
    title: str = Field(..., min_length=1, max_length=255)
    url: str = Field(..., min_length=1, max_length=500)
    employment_type: str = Field(..., min_length=1, max_length=100)
    description: str | None = None


class VacancyCreate(VacancyBase):
    """Схема создания вакансии."""
    rating: int | None = Field(None, ge=1, description="Рейтинг для сортировки (по умолчанию 1)")


class VacancyUpdate(BaseModel):
    """Схема обновления вакансии."""
    title: str | None = Field(None, min_length=1, max_length=255)
    url: str | None = Field(None, min_length=1, max_length=500)
    employment_type: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = None


class VacancyResponse(VacancyBase):
    """Схема ответа с вакансией."""
    id: int
    created_at: datetime
    updated_at: datetime
    is_hidden: bool
    rating: int
    
    class Config:
        from_attributes = True


class VacancyHideUpdate(BaseModel):
    """Схема для скрытия/показа вакансии."""
    is_hidden: bool


class VacancyRatingUpdate(BaseModel):
    """Схема для изменения рейтинга."""
    rating: int = Field(..., ge=0)
