from typing import Optional

from .dto import ApplicantReadDTO
from .domain import Notification, History
from .templates import POSITIVE_MESSAGE, WARNING_MESSAGE, CRITICAL_MESSAGE
from .interfaces import (
    BaseNotificationFactory,
    ProfileRepository,
    HistoryRepository,
    RecommendationSystem
)
from ..constants import (
    POSITIVE_THRESHOLD_PROBABILITY,
    CRITICAL_THRESHOLD_PROBABILITY,
    THRESHOLD_VELOCITY,
    BUDGET_PLACES_FOR_DIRECTIONS,
    WARNING_BUDGET_ZONE_THRESHOLD
)


def check_positive(probability: float, rating: int, direction: str) -> bool:
    return probability >= POSITIVE_THRESHOLD_PROBABILITY \
        and rating < BUDGET_PLACES_FOR_DIRECTIONS[direction] - WARNING_BUDGET_ZONE_THRESHOLD


def check_warning(rating: int, direction: str, history: History) -> bool:
    return history.velocity[-1] <= THRESHOLD_VELOCITY \
        and BUDGET_PLACES_FOR_DIRECTIONS[direction] - rating > WARNING_BUDGET_ZONE_THRESHOLD


def _check_critical(probability: float, rating: int, direction: str) -> bool:
    return probability <= CRITICAL_THRESHOLD_PROBABILITY \
        and rating > BUDGET_PLACES_FOR_DIRECTIONS[direction]


class NotificationFactory(BaseNotificationFactory):
    def __init__(
            self,
            profile_repository: ProfileRepository,
            history_repository: HistoryRepository,
            recommendation_system: RecommendationSystem
    ) -> None:
        self.profile_repository = profile_repository
        self.history_repository = history_repository
        self.recommendation_system = recommendation_system

    async def create(self, applicant: ApplicantReadDTO) -> Optional[Notification]:
        profile = await self.profile_repository.get_by_applicant_id(applicant.applicant_id)
        if not profile:
            return None
        history = await self.history_repository.read(applicant.applicant_id)
        if self._check_positive(applicant.probability, applicant.rating, applicant.direction):
            ...
        elif self._check_warning(applicant.rating, applicant.direction, history):
            ...
        elif self._check_critical(applicant.probability, applicant.rating, applicant.direction):
            ...
        else:
            return None

    @staticmethod
    def _check_positive(probability: float, rating: int, direction: str) -> bool:
        return probability >= POSITIVE_THRESHOLD_PROBABILITY \
            and rating < BUDGET_PLACES_FOR_DIRECTIONS[direction] - WARNING_BUDGET_ZONE_THRESHOLD

    @staticmethod
    def _check_warning(rating: int, direction: str, history: History) -> bool:
        return history.velocity[-1] <= THRESHOLD_VELOCITY \
            and BUDGET_PLACES_FOR_DIRECTIONS[direction] - rating > WARNING_BUDGET_ZONE_THRESHOLD

    @staticmethod
    def _check_critical(probability: float, rating: int, direction: str) -> bool:
        return probability <= CRITICAL_THRESHOLD_PROBABILITY \
            and rating > BUDGET_PLACES_FOR_DIRECTIONS[direction]


class WarningNotificationFactory(BaseNotificationFactory):
    def __init__(
            self,
            profile_repository: ProfileRepository,
            history: History
    ) -> None:
        self.profile_repository = profile_repository
        self.history = history

    async def create(self, applicant: ApplicantReadDTO) -> Optional[Notification]:
        profile = await self.profile_repository.get_by_applicant_id(applicant.applicant_id)
        if profile:
            return Notification(
                level="WARNING",
                user_id=profile.user_id,
                text=WARNING_MESSAGE.format(
                    direction=applicant.direction,
                    probability=applicant.probability,
                    rating=applicant.rating,
                    velocity=self.history.velocity
                )
            )


class CriticalNotificationFactory(BaseNotificationFactory):
    def __init__(
            self,
            profile_repository: ProfileRepository,
            recommendation_system: RecommendationSystem
    ) -> None:
        self.profile_repository = profile_repository
        self.recommendation_system = recommendation_system

    async def create(self, applicant: ApplicantReadDTO) -> Optional[Notification]:
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
