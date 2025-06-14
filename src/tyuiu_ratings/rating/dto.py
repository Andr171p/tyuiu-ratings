from datetime import datetime

from pydantic import Field

from .schemas import Rating


class RatingCreation(Rating):
    """Создание рейтинга"""
    applicant_id: int  # Уникальный ID абитуриента
    direction: str  # Направление подготовки
    date: datetime = Field(default_factory=datetime.today)
