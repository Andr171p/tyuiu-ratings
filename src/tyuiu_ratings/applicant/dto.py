from datetime import datetime

from pydantic import field_validator

from .schemas import Applicant

from ..utils import mapping_direction


class ApplicantUpdateEvent(Applicant):
    """Событие на создание/обновление абитуриента в конкурсном списке."""
    @field_validator("direction")
    def validate_direction(cls, direction: str) -> str:
        return mapping_direction(direction)


class CreatedApplicant(Applicant):
    """Абитуриент из базы данных (уже созданный)"""
    created_at: datetime
    updated_at: datetime
