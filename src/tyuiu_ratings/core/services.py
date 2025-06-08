from typing import Optional

from .dto import ApplicantReadDTO
from .domain import RatingHistory, Notification
from .interfaces import BaseConditionalChecker, ProfileRepository
from .templates import POSITIVE_MESSAGE, WARNING_MESSAGE, CRITICAL_MESSAGE

from ..constants import (
    MAX_CHANGE,
    DAYS_COUNT,
    TOP_RATING,
    RATING_STATUS,
    THRESHOLD_VELOCITY,
    BUDGET_PLACES_FOR_DIRECTIONS,
    WARNING_BUDGET_ZONE_THRESHOLD,
    POSITIVE_THRESHOLD_PROBABILITY,
    CRITICAL_THRESHOLD_PROBABILITY,
)
from ..utils import is_rating_stable


class PositiveConditionalChecker(BaseConditionalChecker):
    def __init__(self, applicant: ApplicantReadDTO, rating_history: RatingHistory) -> None:
        self._applicant = applicant
        self._rating_history = rating_history

    def check(self) -> bool:
        return self._high_probability_conditional or self._rating_stable_conditional

    @property
    def _high_probability_conditional(self) -> bool:
        """Высокая вероятность поступления на бюджет"""
        return self._applicant.probability >= POSITIVE_THRESHOLD_PROBABILITY \
            and self._applicant.rating < BUDGET_PLACES_FOR_DIRECTIONS[self._applicant.direction] \
            - WARNING_BUDGET_ZONE_THRESHOLD

    @property
    def _rating_stable_conditional(self) -> bool:
        """Рейтинг стабилен последние N дней"""
        return is_rating_stable(
            history=self._rating_history.history,
            days_count=DAYS_COUNT,
            max_change=MAX_CHANGE
        ) and self._applicant.rating <= TOP_RATING


class WarningConditionalChecker(BaseConditionalChecker):
    def __init__(self, applicant: ApplicantReadDTO, rating_history: RatingHistory) -> None:
        self._applicant = applicant
        self._rating_history = rating_history

    def check(self) -> bool:
        return self._fast_rating_decrease_conditional or self._in_warning_zone_conditional

    @property
    def _fast_rating_decrease_conditional(self) -> bool:
        """Быстрое падание в рейтинге за последний день"""
        return self._rating_history.velocity[-1] <= THRESHOLD_VELOCITY

    @property
    def _in_warning_zone_conditional(self) -> bool:
        """Абитуриент приближается к зоне вылета из конкурса"""
        return BUDGET_PLACES_FOR_DIRECTIONS[self._applicant.direction] \
            - self._applicant.rating > WARNING_BUDGET_ZONE_THRESHOLD


class CriticalConditionalChecker(BaseConditionalChecker):
    def __init__(self, applicant: ApplicantReadDTO, rating_history: RatingHistory) -> None:
        self._applicant = applicant
        self._rating_history = rating_history

    def check(self) -> bool:
        return self._low_probability_conditional or self._not_in_budget_zone_conditional

    @property
    def _low_probability_conditional(self) -> bool:
        """Очень низкая вероятность поступления на бюджет"""
        return self._applicant.probability <= CRITICAL_THRESHOLD_PROBABILITY

    @property
    def _not_in_budget_zone_conditional(self) -> bool:
        """Абитуриент больше не проходит на бюджет"""
        return self._applicant.rating > BUDGET_PLACES_FOR_DIRECTIONS[self._applicant.direction]


class NotificationMaker:
    def __init__(self, profile_repository: ProfileRepository) -> None:
        self._profile_repository = profile_repository

    async def create(
            self,
            applicant: ApplicantReadDTO,
            rating_history: RatingHistory
    ) -> Optional[Notification]:
        profile = await self._profile_repository.get_by_applicant_id(applicant.applicant_id)
        if not profile:
            return None
        positive_checker = PositiveConditionalChecker(applicant, rating_history)
        if positive_checker.check():
            return Notification(
                level="POSITIVE",
                user_id=profile.user_id,
                text=POSITIVE_MESSAGE.format(...)
            )
        warning_checker = WarningConditionalChecker(applicant, rating_history)
        if warning_checker.check():
            return Notification(
                level="WARNING",
                user_id=profile.user_id,
                text=WARNING_MESSAGE.format(...)
            )
        critical_checker = CriticalConditionalChecker(applicant, rating_history)
        if critical_checker.check():
            return Notification(
                level="CRITICAL",
                user_id=profile.user_id,
                text=CRITICAL_MESSAGE.format()
            )

    async def __call__(
            self,
            applicant: ApplicantReadDTO,
            rating_history: RatingHistory
    ) -> Optional[Notification]:
        return await self.create(applicant, rating_history)


def get_rating_status(applicant: ApplicantReadDTO, rating_history: RatingHistory) -> RATING_STATUS:
    positive_checker = PositiveConditionalChecker(applicant, rating_history)
    if positive_checker.check():
        return "POSITIVE"
    warning_checker = WarningConditionalChecker(applicant, rating_history)
    if warning_checker.check():
        return "WARNING"
    critical_checker = CriticalConditionalChecker(applicant, rating_history)
    if critical_checker.check():
        return "CRITICAL"
    else:
        return "OK"
