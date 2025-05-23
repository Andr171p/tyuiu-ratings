from typing import Optional

from uuid import UUID

from .dto import ApplicantReadDTO
from .domain import Notification, RatingHistory
from .templates import POSITIVE_MESSAGE, WARNING_MESSAGE, CRITICAL_MESSAGE
from .interfaces import (
    BaseNotificationSender,
    ProfileRepository,
    HistoryRepository,
    RecommendationSystem,
    AMQPBroker
)
from ..constants import (
    POSITIVE_THRESHOLD_PROBABILITY,
    CRITICAL_THRESHOLD_PROBABILITY,
    THRESHOLD_VELOCITY,
    BUDGET_PLACES_FOR_DIRECTIONS,
    WARNING_BUDGET_ZONE_THRESHOLD
)


def check_warning(rating: int, direction: str, history: RatingHistory) -> bool:
    return history.velocity[-1] <= THRESHOLD_VELOCITY \
        and BUDGET_PLACES_FOR_DIRECTIONS[direction] - rating > WARNING_BUDGET_ZONE_THRESHOLD


def _check_critical(probability: float, rating: int, direction: str) -> bool:
    return probability <= CRITICAL_THRESHOLD_PROBABILITY \
        and rating > BUDGET_PLACES_FOR_DIRECTIONS[direction]


class PositiveNotificationSender(BaseNotificationSender):
    def __init__(self, broker: AMQPBroker) -> None:
        self.broker = broker

    @staticmethod
    def _check_positive_conditional(probability: float, rating: int, direction: str) -> bool:
        return probability >= POSITIVE_THRESHOLD_PROBABILITY \
            and rating < BUDGET_PLACES_FOR_DIRECTIONS[direction] - WARNING_BUDGET_ZONE_THRESHOLD

    async def send(self, user_id: UUID, applicant: ApplicantReadDTO) -> None:
        if not self._check_positive_conditional(
            probability=applicant.probability,
            rating=applicant.rating,
            direction=applicant.direction
        ):
            return None
        notification = Notification(
            level=POSITIVE_MESSAGE,
            user_id=user_id,
            text=POSITIVE_MESSAGE.format(
                probability=applicant.probability,
                direction=applicant.direction
            ),
        )
        await self.broker.publish(notification)
