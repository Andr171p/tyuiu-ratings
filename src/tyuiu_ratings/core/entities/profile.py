from uuid import UUID
from typing import List, Literal

from pydantic import BaseModel, Field

from src.tyuiu_ratings.constants import (
    MIN_GPA,
    MAX_GPA,
    MIN_EXAM_POINTS,
    MAX_EXAM_POINTS
)


class Exam(BaseModel):
    subject: str
    points: int = Field(ge=MIN_EXAM_POINTS, le=MAX_EXAM_POINTS)


class Profile(BaseModel):
    user_id: UUID
    applicant_id: int
    gender: Literal["male", "female"]
    gpa: float = Field(ge=MIN_GPA, le=MAX_GPA)
    exams: List[Exam]
