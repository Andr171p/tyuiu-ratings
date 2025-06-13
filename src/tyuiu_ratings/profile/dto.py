from typing import Literal, Optional

from datetime import datetime

from pydantic import BaseModel, Field

from .schemas import Profile, Exam

from ..constants import MIN_GPA, MAX_GPA


class CreatedProfile(Profile):
    """Уже созданный профиль"""
    created_at: datetime
    updated_at: datetime


class ProfileRefactoring(BaseModel):
    """Редактируемый профиль"""
    applicant_id: Optional[int] = None
    gender: Optional[Literal["male", "female"]] = None
    gpa: Optional[float] = Field(
        default=None,
        ge=MIN_GPA,
        le=MAX_GPA,
        validate_default=True
    )
    exams: Optional[list[Exam]] = None
