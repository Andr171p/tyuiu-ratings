from typing import Optional

from uuid import UUID

from ...domain import RatingHistory
from ...factories import get_rating_status
from ...dto import ApplicantRatingHistoryDTO
from ...base import ApplicantRepository, ProfileRepository, RatingRepository

from src.tyuiu_ratings.utils import calculate_velocity


class GetRatingHistoryUseCase:
    """Чтение истории изменения рейтинга."""
    def __init__(
            self,
            profile_repository: ProfileRepository,
            applicant_repository: ApplicantRepository,
            rating_repository: RatingRepository
    ) -> None:
        self._profile_repository = profile_repository
        self._applicant_repository = applicant_repository
        self._rating_repository = rating_repository

    async def get(
            self,
            user_id: UUID,
            direction: str
    ) -> Optional[ApplicantRatingHistoryDTO]:
        profile = await self._profile_repository.read(user_id)
        if not profile:
            return None
        ratings = await self._rating_repository.read(profile.applicant_id, direction)
        applicant = await self._applicant_repository.read(profile.applicant_id)
        last_change = int(calculate_velocity(ratings)[-1])
        status = get_rating_status(
            applicant=applicant,
            rating_history=RatingHistory(ratings=ratings)
        )
        applicant_rating_history = ApplicantRatingHistoryDTO(
            applicant_id=profile.applicant_id,
            direction=direction,
            last_change=last_change,
            status=status,
            ratings=ratings
        )
        return applicant_rating_history
