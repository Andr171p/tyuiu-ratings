from typing import Optional

from uuid import UUID

from .schemas import Rating


class RatingCreation(Rating):
    """Создание рейтинга"""
    user_id: Optional[UUID] = None
    applicant_id: int  # Уникальный ID абитуриента
    direction: str  # Направление подготовки
