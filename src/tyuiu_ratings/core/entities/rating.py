from datetime import datetime

from typing import List

from pydantic import BaseModel, Field

from src.tyuiu_ratings.constants import (
    MIN_POINTS,
    MAX_POINTS,
    MIN_PRIORITY,
    MAX_PRIORITY,
    MIN_BONUS_POINTS,
    MAX_BONUS_POINTS
)


class Applicant(BaseModel):
    applicant_id: int  # Уникальный код абитуриента
    institute: str  # Институт
    direction: str  # Направление подготовки
    priority: int = Field(ge=MIN_PRIORITY, le=MAX_PRIORITY)  # Приоритет
    points: int = Field(ge=MIN_POINTS, le=MAX_POINTS)  # Сумма баллов ЕГЭ
    bonus_points: int = Field(ge=MIN_BONUS_POINTS, le=MAX_BONUS_POINTS)  # Дополнительные баллы
    original: bool  # Сдан оригинал


class Rating(BaseModel):
    institute: str
    direction: str
    rating: List[Applicant]


class Place(BaseModel):
    rating: int
    date: datetime


class History(BaseModel):
    applicant_id: int
    history: List[Place]
