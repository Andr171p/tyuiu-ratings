from datetime import datetime

from pydantic import BaseModel

from ..entities import Profile, Applicant


class ProfileReadDTO(Profile):
    created_at: datetime
    updated_at: datetime


class ApplicantReadDTO(Applicant):
    created_at: datetime
    updated_at: datetime
