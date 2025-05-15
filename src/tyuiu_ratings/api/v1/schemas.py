from pydantic import BaseModel

from src.tyuiu_ratings.core.dto import ApplicantReadDTO


class ApplicantsResponse(BaseModel):
    applicants: list[ApplicantReadDTO]
