"""Модель отзывов."""
from sqlalchemy import String, Text, Integer
from sqlalchemy.orm import Mapped, mapped_column

from models.base import BaseModel


class Review(BaseModel):
    """Модель отзыва."""
    
    __tablename__ = "reviews"
    
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    company: Mapped[str] = mapped_column(String(255), nullable=False)
    review_text: Mapped[str] = mapped_column(Text, nullable=False)
    stars: Mapped[int] = mapped_column(Integer, nullable=False)
    photo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
