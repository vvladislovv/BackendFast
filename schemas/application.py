"""Схемы для заявок."""
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr


class ApplicationCreate(BaseModel):
    """Схема создания заявки."""
    name: str = Field(..., min_length=1, max_length=255, description="Имя клиента")
    company: str | None = Field(None, max_length=255, description="Название компании")
    email: EmailStr = Field(..., description="Email клиента")
    phone: str | None = Field(None, max_length=50, description="Телефон клиента")
    message: str = Field(..., min_length=1, description="Сообщение от клиента")
    file_path: str | None = Field(None, max_length=500, description="Путь к загруженному файлу")


class ApplicationResponse(BaseModel):
    """Схема ответа заявки."""
    id: int
    name: str
    company: str | None
    email: str
    phone: str | None
    message: str
    file_path: str | None
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
