from typing import Literal

from datetime import datetime

from pydantic import BaseModel, Field, field_validator, ConfigDict

from .schemas import Applicant

from ..types import ExamList
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
    probability: float  # Вероятность поступления


class CreatedApplicant(Applicant):
    """Абитуриент из базы данных (уже созданный)"""
    probability: float
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
    exams: ExamList

    model_config = ConfigDict(from_attributes=True)


class Prediction(BaseModel):
    """Предсказание вероятности поступления на направление подготовки"""
    direction: str
    probability: float


class Recommendation(BaseModel):
    direction_id: int
    direction: str


class RerankedPriority(BaseModel):
    """Ре ранжированное направление подготовки по вероятности поступления"""
    priority: int
    direction: str
    probability: float


class PredictedRecommendation(BaseModel):
    """Рекомендация с вероятностью поступления"""
    direction_id: int
    direction: str
    probability: float
    status: Literal["BETTER", "SAME", "LESS"] = "SAME"  # BETTER если рекомендация лучше текущего выбора


class CompetitionList(BaseModel):
    """Конкурсный список абитуриентов на конкретное направление"""
    applicant_id: int
    institute: str
    direction: str
    applicants: list[CreatedApplicant]
