from uuid import UUID
from datetime import datetime

from typing import List

from pydantic import BaseModel


class Subject(BaseModel):
    name: str
    points: int


class Profile(BaseModel):
    user_id: UUID
    applicant_id: int
    gpa: float
    subjects: List[Subject]


class Applicant(BaseModel):
    applicant_id: int  # Уникальный код абитуриента
    institute: str  # Институт
    direction: str  # Направление подготовки
    points: int  # Сумма баллов
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
