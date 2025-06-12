from typing import Literal, TYPE_CHECKING

if TYPE_CHECKING:
    from ..profile.schemas import Exam

from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from .schemas import Applicant

from ..utils import mapping_direction
from ..constants import (
    PREDICTED_YEAR,
    DEFAULT_GPA,
    DEFAULT_GENDER,
    MIN_POINTS,
    MAX_POINTS,
    MIN_GPA,
    MAX_GPA
)


class ApplicantUpdateEvent(Applicant):
    """Событие на создание/обновление абитуриента в конкурсном списке."""
    @field_validator("direction")
    def validate_direction(cls, direction: str) -> str:
        return mapping_direction(direction)


class ApplicantCreate(Applicant):
    """Модель для создания ресурса"""
    probability: float


class CreatedApplicant(Applicant):
    """Абитуриент из базы данных (уже созданный)"""
    created_at: datetime
    updated_at: datetime


class ApplicantPredict(BaseModel):
    """Схема запроса для получения вероятности поступления"""
    year: int = PREDICTED_YEAR
    gender: Literal["male", "female"] = DEFAULT_GENDER
    gpa: float = DEFAULT_GPA
    points: int = Field(ge=MIN_POINTS, le=MAX_POINTS)
    direction: str


class ApplicantRecommend(BaseModel):
    """Схема запроса для получения рекомендаций"""
    gender: Literal["male", "female"] = DEFAULT_GENDER
    gpa: float = Field(ge=MIN_GPA, le=MAX_GPA)
    points: int = Field(ge=MIN_POINTS, le=MAX_POINTS)
    exams: list["Exam"]


class Prediction(BaseModel):
    """Предсказание вероятности поступления на направление подготовки"""
    direction: str
    probability: float


class Recommendation(BaseModel):
    direction_id: int
    direction: str
