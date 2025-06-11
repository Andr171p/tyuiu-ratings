from typing import Literal, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .dto import ApplicantCreateDTO

from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from ..utils import (
    calculate_velocity,
    calculate_mean_velocity,
    calculate_acceleration,
    calculate_stability,
    mapping_direction
)
from ..constants import (
    MIN_GPA,
    MAX_GPA,
    MIN_POINTS,
    MAX_POINTS,
    MIN_PRIORITY,
    MAX_PRIORITY,
    MIN_BONUS_POINTS,
    MAX_BONUS_POINTS,
    MIN_EXAM_POINTS,
    MAX_EXAM_POINTS,
    SUBJECT,
    NOTIFICATION_LEVEL
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
    original: bool  # Сдан оригинал

    @field_validator("direction")
    def validate_direction(cls, direction: str) -> str:
        return mapping_direction(direction)

    def to_create_dto(self, probability: float) -> "ApplicantCreateDTO":
        from .dto import ApplicantCreateDTO
        return ApplicantCreateDTO(
            applicant_id=self.applicant_id,
            rank=self.rank,
            institute=self.institute,
            direction=self.direction,
            priority=self.priority,
            points=self.points,
            bonus_points=self.bonus_points,
            original=self.original,
            probability=probability
        )


class CompetitionList(BaseModel):
    """Конкурсный список абитуриентов на конкретное направление"""
    applicant_id: int
    institute: str
    direction: str
    applicants: list[Applicant]


class Rating(BaseModel):
    """Позиция в рейтинге за конкретный день"""
    rank: int
    date: datetime


class RatingHistory(BaseModel):
    """История изменения рейтинга"""
    ratings: list[Rating]

    @property
    def velocity(self) -> list[float]:
        return calculate_velocity(self.ratings)

    @property
    def mean_velocity(self) -> float:
        return calculate_mean_velocity(self.ratings)

    @property
    def acceleration(self) -> list[float]:
        return calculate_acceleration(self.ratings)

    @property
    def stability(self) -> float:
        return calculate_stability(self.ratings)


class Exam(BaseModel):
    """Экзамен ЕГЭ"""
    subject: SUBJECT
    points: int = Field(ge=MIN_EXAM_POINTS, le=MAX_EXAM_POINTS)


class Profile(BaseModel):
    """Профиль абитуриента"""
    user_id: UUID  # Уникальный ID пользователя получаемый при регистрации
    applicant_id: int
    gender: Literal["male", "female"]
    gpa: float = Field(ge=MIN_GPA, le=MAX_GPA)
    exams: list[Exam]


class Notification(BaseModel):
    """Уведомление для абитуриента"""
    level: NOTIFICATION_LEVEL
    user_id: UUID
    photo: Optional[str] = None
    text: str
