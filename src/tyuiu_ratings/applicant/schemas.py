from pydantic import BaseModel, Field

from ..constants import (
    MIN_POINTS,
    MAX_POINTS,
    MIN_PRIORITY,
    MAX_PRIORITY,
    MIN_BONUS_POINTS,
    MAX_BONUS_POINTS
)


class Applicant(BaseModel):
    """Абитуриент, участник конкурсного списка"""
    applicant_id: int  # Уникальный код абитуриента
    rank: int  # Место в рейтинге
    institute: str  # Институт
    direction: str  # Направление подготовки
    priority: int = Field(ge=MIN_PRIORITY, le=MAX_PRIORITY)  # Приоритет
    points: int = Field(ge=MIN_POINTS, le=MAX_POINTS)  # Сумма баллов ЕГЭ
    bonus_points: int = Field(ge=MIN_BONUS_POINTS, le=MAX_BONUS_POINTS)  # Дополнительные баллы
    original: bool  # Сдан оригинал (True если сдан, False если нет)
