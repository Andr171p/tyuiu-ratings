from collections.abc import AsyncIterable

from uuid import UUID

from .domain import Notification
from .dto import ApplicantReadDTO
from .interfaces import Notifier, ApplicantRepository, ProfileRepository
from ..utils import calculate_pages
from ..constants import DEFAULT_LIMIT, THRESHOLD_PROBABILITY


class PositiveNotifier(Notifier):
    def __init__(
            self,
            applicant_repository: ApplicantRepository,
            profile_repository: ProfileRepository
    ) -> None:
        self.applicant_repository = applicant_repository
        self.profile_repository = profile_repository

    async def get_notifications(self) -> AsyncIterable[Notification]:
        async for applicant in self._paginated_applicants():
            if applicant.probability >= THRESHOLD_PROBABILITY:
                profile = await self.profile_repository.get_by_applicant_id(applicant.applicant_id)
                if profile:
                    yield Notification(
                        level="POSITIVE",
                        user_id=profile.user_id,
                        text="У вас высокая вероятность поступления"
                    )

    async def _paginated_applicants(self) -> AsyncIterable[ApplicantReadDTO]:
        total_count = await self.applicant_repository.count()
        pages_count = calculate_pages(total_count, DEFAULT_LIMIT)
        for page in range(1, pages_count + 1):
            applicants = await self.applicant_repository.paginate(page, DEFAULT_LIMIT)
            for applicant in applicants:
                yield applicant

    def create_positive_notification(
            self,
            user_id: UUID,
            direction: str,
            probability: float
    ) -> Notification:
        ...
