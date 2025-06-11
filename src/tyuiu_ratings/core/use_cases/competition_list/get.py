from typing import Optional

from uuid import UUID

from ...constants import DIRECTION
from ...domain import CompetitionList
from ...base import ApplicantRepository, ProfileRepository


class GetCompetitionListUseCase:
    """Читает конкурсные списки абитуриентов."""
    def __init__(
            self,
            profile_repository: ProfileRepository,
            applicant_repository: ApplicantRepository
    ) -> None:
        self._profile_repository = profile_repository
        self._applicant_repository = applicant_repository

    async def get(
            self,
            user_id: UUID,
            direction: DIRECTION
    ) -> Optional[CompetitionList]:
        profile = await self._profile_repository.read(user_id)
        applicants = await self._applicant_repository.get_by_direction(direction)
        return CompetitionList(
            applicant_id=profile.applicant_id,
            institute=applicants[0].institute,
            direction=direction,
            applicants=applicants
        )
