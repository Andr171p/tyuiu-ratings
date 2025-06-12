from typing import Optional

from uuid import UUID
from datetime import datetime

from pydantic import Field

from .schemas import Rating


class RatingCreation(Rating):
    """Создание рейтинга"""
    user_id: Optional[UUID] = None
    applicant_id: int  # Уникальный ID абитуриента
    direction: str  # Направление подготовки
    date: datetime = Field(default_factory=datetime.today)
