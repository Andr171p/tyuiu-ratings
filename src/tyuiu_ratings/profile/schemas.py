from typing import Literal

from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict

from ..constants import MIN_GPA, MAX_GPA, MIN_EXAM_POINTS, MAX_EXAM_POINTS, SUBJECT


class Exam(BaseModel):
    """Экзамен ЕГЭ"""
    subject: SUBJECT  # Название предмета
    points: int = Field(ge=MIN_EXAM_POINTS, le=MAX_EXAM_POINTS)  # Количество баллов за предмет


class Profile(BaseModel):
    """Профиль абитуриента"""
    user_id: UUID  # Уникальный ID пользователя получаемый при регистрации
    applicant_id: int  # Уникальный ID абитуриента
    gender: Literal["male", "female"]  # Пол абитуриента (используется для более точных рекомендаций)
    gpa: float = Field(ge=MIN_GPA, le=MAX_GPA)  # Средний балл аттестата
    exams: list[Exam]

    model_config = ConfigDict(from_attributes=True)
