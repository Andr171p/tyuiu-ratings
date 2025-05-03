from uuid import UUID
from datetime import datetime

from typing import List

from pydantic import BaseModel, Field

from src.tyuiu_ratings.constants import (
    MIN_GPA,
    MAX_GPA,
    MIN_POINTS,
    MAX_POINTS,
    MIN_EXAM_POINTS,
    MAX_EXAM_POINTS,
    MIN_BONUS_POINTS,
    MAX_BONUS_POINTS
)


class Exam(BaseModel):
    name: str
    points: int = Field(ge=MIN_EXAM_POINTS, le=MAX_EXAM_POINTS)


class DirectionCompetition(BaseModel):
    direction: str
    budget_places: int


class Profile(BaseModel):
    user_id: UUID
    applicant_id: int
    gpa: float = Field(ge=MIN_GPA, le=MAX_GPA)
    exams: List[Exam]


class Applicant(BaseModel):
    applicant_id: int  # Уникальный код абитуриента
    institute: str  # Институт
    direction: str  # Направление подготовки
    points: int = Field(ge=MIN_POINTS, le=MAX_POINTS)  # Сумма баллов ЕГЭ
    bonus_points: int = Field(ge=MIN_BONUS_POINTS, le=MAX_BONUS_POINTS)  # Дополнительные баллы
    original: bool  # Сдан оригинал


class Rating(BaseModel):
    institute: str
    direction: str
    rating: List[Applicant]


class Place(BaseModel):
    applicant_id: int
    rating: int
    date: datetime


class History(BaseModel):
    applicant_id: int
    history: List[Place]
