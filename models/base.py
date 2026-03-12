"""Базовая модель с общими полями."""
from datetime import datetime, timezone

from sqlalchemy import DateTime, Integer, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from core.database import Base


class BaseModel(Base):
    """Базовая модель с общими полями для всех таблиц."""
    
    __abstract__ = True
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    is_hidden: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    rating: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
