from typing import Optional

from abc import ABC, abstractmethod

from pydantic import BaseModel

from .enums import NotificationLevel

from ..rating.schemas import Rating
from ..applicant.dto import CreatedApplicant
from ..utils import is_rating_stable, calculate_velocity
from ..constants import (
    MAX_CHANGE,
    DAYS_COUNT,
    TOP_RATING,
    THRESHOLD_VELOCITY,
    BUDGET_PLACES_FOR_DIRECTIONS,
    WARNING_BUDGET_ZONE_THRESHOLD,
    POSITIVE_THRESHOLD_PROBABILITY,
    CRITICAL_THRESHOLD_PROBABILITY,
)


class ConditionalResult(BaseModel):
    level: NotificationLevel
    message: str


class ConditionalHandler(ABC):
    def __init__(self, next_handler: Optional["ConditionalHandler"]) -> None:
        self.next_handler = next_handler

    @abstractmethod
    def check(
            self,
            applicant: CreatedApplicant,
            ratings: list[Rating]
    ) -> Optional[ConditionalResult]:
        """Логика проверки условия для формирования уведомления."""
        pass

    async def handle(
            self,
            applicant: CreatedApplicant,
            ratings: list[Rating]
    ) -> Optional[ConditionalResult]:
        result = self.check(applicant, ratings)
        if result:
            return result
        if self.next_handler:
            return self.next_handler.handle(applicant, ratings)
        return None


class PositiveConditionalHandler(ConditionalHandler):
    def check(
            self,
            applicant: CreatedApplicant,
            ratings: list[Rating]
    ) -> Optional[ConditionalResult]:
        if self._high_probability(applicant) and self._rating_stable(applicant, ratings):
            return ConditionalResult(
                level=NotificationLevel.POSITIVE,
                message=...
            )
        return None

    @staticmethod
    def _high_probability(applicant: CreatedApplicant) -> bool:
        """Высокая вероятность поступления на бюджет"""
        return applicant.probability >= POSITIVE_THRESHOLD_PROBABILITY \
            and applicant.rank < BUDGET_PLACES_FOR_DIRECTIONS[applicant.direction] \
            - WARNING_BUDGET_ZONE_THRESHOLD

    @staticmethod
    def _rating_stable(applicant: CreatedApplicant, ratings: list[Rating]) -> bool:
        """Рейтинг стабилен последние N дней"""
        return is_rating_stable(
            ratings=ratings,
            days_count=DAYS_COUNT,
            max_change=MAX_CHANGE
        ) and applicant.rank <= TOP_RATING


class WarningConditionalHandler(ConditionalHandler):
    def check(
            self,
            applicant: CreatedApplicant,
            ratings: list[Rating]
    ) -> Optional[ConditionalResult]:
        if self._fast_rating_decrease_conditional(ratings) or self._in_warning_zone_conditional(applicant):
            return ConditionalResult(
                level=NotificationLevel.WARNING,
                message=...
            )
        return None

    @staticmethod
    def _fast_rating_decrease_conditional(ratings: list[Rating]) -> bool:
        """Быстрое падание в рейтинге за последний день"""
        return calculate_velocity(ratings)[-1] <= THRESHOLD_VELOCITY

    @staticmethod
    def _in_warning_zone_conditional(applicant: CreatedApplicant) -> bool:
        """Абитуриент приближается к зоне вылета из конкурса"""
        return BUDGET_PLACES_FOR_DIRECTIONS[applicant.direction] \
            - applicant.rank > WARNING_BUDGET_ZONE_THRESHOLD


class CriticalConditionalHandler(ConditionalHandler):
    def check(
            self,
            applicant: CreatedApplicant,
            ratings: list[Rating]
    ) -> Optional[ConditionalResult]:
        if self._low_probability_conditional(applicant) or self._not_in_budget_zone_conditional(applicant):
            return ConditionalResult(
                level=NotificationLevel.CRITICAL,
                message=...
            )
        return None

    @staticmethod
    def _low_probability_conditional(applicant: CreatedApplicant) -> bool:
        """Очень низкая вероятность поступления на бюджет"""
        return applicant.probability <= CRITICAL_THRESHOLD_PROBABILITY

    @staticmethod
    def _not_in_budget_zone_conditional(applicant: CreatedApplicant) -> bool:
        """Абитуриент больше не проходит на бюджет"""
        return applicant.rating > BUDGET_PLACES_FOR_DIRECTIONS[applicant.direction]
