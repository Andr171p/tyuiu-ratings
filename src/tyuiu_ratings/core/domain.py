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
    AVAILABLE_SUBJECTS,
    NOTIFICATION_LEVELS
)


class Applicant(BaseModel):
    applicant_id: int  # Уникальный код абитуриента
    rating: int  # Место в рейтинге
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
            rating=self.rating,
            institute=self.institute,
            direction=self.direction,
            priority=self.priority,
            points=self.points,
            bonus_points=self.bonus_points,
            original=self.original,
            probability=probability
        )


class Rating(BaseModel):
    institute: str
    direction: str
    rating: list[Applicant]


class Rank(BaseModel):
    applicant_id: int
    rating: int
    date: datetime


class History(BaseModel):
    applicant_id: int
    history: list[Rank]

    @property
    def velocity(self) -> list[float]:
        return calculate_velocity(self.history)

    @property
    def mean_velocity(self) -> float:
        return calculate_mean_velocity(self.history)

    @property
    def acceleration(self) -> list[float]:
        return calculate_acceleration(self.history)

    @property
    def stability(self) -> float:
        return calculate_stability(self.history)


class Exam(BaseModel):
    subject: AVAILABLE_SUBJECTS
    points: int = Field(ge=MIN_EXAM_POINTS, le=MAX_EXAM_POINTS)


class Profile(BaseModel):
    user_id: UUID
    applicant_id: int
    gender: Literal["male", "female"]
    gpa: float = Field(ge=MIN_GPA, le=MAX_GPA)
    exams: list[Exam]


class Notification(BaseModel):
    level: NOTIFICATION_LEVELS
    user_id: UUID
    photo: Optional[str] = None
    text: str
