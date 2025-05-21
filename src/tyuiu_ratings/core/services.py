from typing import Optional

from .dto import ApplicantReadDTO
from .domain import Notification, History
from .templates import POSITIVE_MESSAGE, WARNING_MESSAGE, CRITICAL_MESSAGE
from .interfaces import (
    BaseNotifier,
    ProfileRepository,
    HistoryRepository,
    RecommendationSystem
)
from ..constants import (
    POSITIVE_THRESHOLD_PROBABILITY,
    CRITICAL_THRESHOLD_PROBABILITY,
    THRESHOLD_VELOCITY,
    BUDGET_PLACES_FOR_DIRECTIONS,
    BUDGET_ZONE_THRESHOLD
)


class PositiveNotifier(BaseNotifier):
    def __init__(self, profile_repository: ProfileRepository) -> None:
        self.profile_repository = profile_repository

    async def create_notification(self, applicant: ApplicantReadDTO) -> Optional[Notification]:
        if not await self._check_conditional(applicant):
            return None
        profile = await self.profile_repository.get_by_applicant_id(applicant.applicant_id)
        if profile:
            return Notification(
                level="POSITIVE",
                user_id=profile.user_id,
                text=POSITIVE_MESSAGE.format(
                    direction=applicant.direction,
                    probability=applicant.probability
                )
            )

    async def _check_conditional(self, applicant: ApplicantReadDTO) -> bool:
        return applicant.probability >= POSITIVE_THRESHOLD_PROBABILITY


class WarningNotifier(BaseNotifier):
    def __init__(
            self,
            profile_repository: ProfileRepository,
            history_repository: HistoryRepository
    ) -> None:
        self.profile_repository = profile_repository
        self.history_repository = history_repository

    async def create_notification(self, applicant: ApplicantReadDTO) -> Optional[Notification]:
        ranks = await self.history_repository.read(applicant.applicant_id)
        history = History(applicant_id=applicant.applicant_id, history=ranks)
        if not await self._check_conditional(history):
            return None
        profile = await self.profile_repository.get_by_applicant_id(applicant.applicant_id)
        if profile:
            return Notification(
                level="WARNING",
                user_id=profile.user_id,
                text=WARNING_MESSAGE.format(
                    direction=applicant.direction,
                    probability=applicant.probability,
                    rating=applicant.rating,
                    velocity=history.velocity
                )
            )

    async def _check_conditional(self, history: History) -> bool:
        last_velocity = history.velocity[-1]
        return last_velocity <= THRESHOLD_VELOCITY


class CriticalNotifier(BaseNotifier):
    def __init__(
            self,
            profile_repository: ProfileRepository,
            recommendation_system: RecommendationSystem
    ) -> None:
        self.profile_repository = profile_repository
        self.recommendation_system = recommendation_system

    async def create_notification(self, applicant: ApplicantReadDTO) -> Optional[Notification]:
        if not await self._check_conditional(applicant):
            return None
        profile = await self.profile_repository.get_by_applicant_id(applicant.applicant_id)
        if profile:
            return Notification(
                level="CRITICAL",
                user_id=profile.user_id,
                text=CRITICAL_MESSAGE.format(
                    direction=applicant.direction,
                    probability=applicant.probability
                )
            )

    async def _check_conditional(self, applicant: ApplicantReadDTO) -> bool:
        return applicant.probability <= CRITICAL_THRESHOLD_PROBABILITY \
            or applicant.rating < BUDGET_PLACES_FOR_DIRECTIONS[applicant.direction]
