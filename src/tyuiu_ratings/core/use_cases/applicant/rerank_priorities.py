from uuid import UUID

from ...dto import RerankedPriorityDTO
from ...base import ApplicantRepository, ProfileRepository


class RerankPrioritiesUseCase:
    """
    Переставляет приоритеты абитуриента так,
    чтобы вероятность поступления была наиболее высокой.
    """
    def __init__(
            self,
            applicant_repository: ApplicantRepository,
            profile_repository: ProfileRepository
    ) -> None:
        self._applicant_repository = applicant_repository
        self._profile_repository = profile_repository

    async def rerank(self, user_id: UUID) -> list[RerankedPriorityDTO]:
        profile = await self._profile_repository.read(user_id)
        applicants = await self._applicant_repository.sort_by_probability(profile.applicant_id)
        return [
            RerankedPriorityDTO(
                priority=applicant.priority,
                direction=applicant.direction,
                probability=applicant.probability
            )
            for applicant in applicants
        ]
