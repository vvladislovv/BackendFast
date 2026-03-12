"""Модель кейсов."""
from sqlalchemy import String, Text, Boolean, ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from models.base import BaseModel


class Case(BaseModel):
    """Модель кейса/портфолио."""
    
    __tablename__ = "cases"
    
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    about: Mapped[str] = mapped_column(Text, nullable=False)
    tags: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False, default=list)
    image_url: Mapped[str] = mapped_column(String(500), nullable=False)
    link_url: Mapped[str] = mapped_column(String(500), nullable=False)
    is_fresh: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
