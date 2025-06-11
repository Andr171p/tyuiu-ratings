from typing import Literal

from datetime import datetime

from pydantic import BaseModel, Field

from .domain import Profile, Exam, Applicant, Rating, RatingHistory
from ..constants import (
    MIN_GPA,
    MAX_GPA,
    MIN_POINTS,
    MAX_POINTS,
    PREDICTED_YEAR,
    DEFAULT_GPA,
    DEFAULT_GENDER,
    RATING_STATUS
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
    gender: Literal["male", "female"] = DEFAULT_GENDER
    gpa: float = DEFAULT_GPA
    points: int = Field(ge=MIN_POINTS, le=MAX_POINTS)
    direction: str


class ApplicantRecommendDTO(BaseModel):
    gender: Literal["male", "female"] = "male"
    gpa: float = Field(ge=MIN_GPA, le=MAX_GPA)
    points: int = Field(ge=MIN_POINTS, le=MAX_POINTS)
    exams: list[Exam]


class RatingCreateDTO(Rating):
    applicant_id: int


class RecommendationDTO(BaseModel):
    direction_id: int
    direction: str


class PredictionDTO(BaseModel):
    direction: str
    probability: float


class PredictedRecommendationDTO(BaseModel):
    direction_id: int
    direction: str
    probability: float
    status: Literal["BETTER", "SAME"] = "SAME"


class RerankedPriorityDTO(BaseModel):
    priority: int
    direction: str
    probability: float


class ApplicantRatingHistoryDTO(RatingHistory):
    applicant_id: int
    direction: str
    last_change: int
    status: RATING_STATUS
