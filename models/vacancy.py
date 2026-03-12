"""Модель вакансий."""
from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from models.base import BaseModel


class Vacancy(BaseModel):
    """Модель вакансии."""
    
    __tablename__ = "vacancies"
    
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    employment_type: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
