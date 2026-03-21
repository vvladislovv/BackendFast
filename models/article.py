"""Модель статей."""
from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from models.base import BaseModel


class Article(BaseModel):
    """Модель статьи."""
    
    __tablename__ = "articles"
    
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    photo: Mapped[str | None] = mapped_column(String(500), nullable=True)
