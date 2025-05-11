from datetime import datetime
from typing import List, Literal

from pydantic import BaseModel, Field

from .entities import Profile, Exam, Applicant
from src.tyuiu_ratings.constants import (
    MIN_GPA,
    MAX_GPA,
    MIN_POINTS,
    MAX_POINTS,
    PREDICTED_YEAR,
    DEFAULT_GPA
)


class ProfileReadDTO(Profile):
    created_at: datetime
    updated_at: datetime


class ApplicantCreateDTO(Applicant):
    probability: float


class ApplicantReadDTO(Applicant):
    probability: float
    created_at: datetime
    updated_at: datetime


class ApplicantPredictDTO(BaseModel):
    year: int = PREDICTED_YEAR
    gender: Literal["male", "female"] = "male"
    gpa: float = DEFAULT_GPA
    points: int = Field(ge=MIN_POINTS, le=MAX_POINTS)
    direction: str


class ApplicantRecommendDTO(BaseModel):
    gender: Literal["male", "female"]
    gpa: float = Field(ge=MIN_GPA, le=MAX_GPA)
    points: int = Field(ge=MIN_POINTS, le=MAX_POINTS)
    exams: List[Exam]


class RecommendedDirectionDTO(BaseModel):
    direction_id: int
    name: str
