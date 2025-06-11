from typing import Optional
from collections.abc import AsyncGenerator

import asyncio

from ...dto import ApplicantReadDTO
from ...constants import DEFAULT_LIMIT
from ...factories import NotificationFactory
from ...domain import Notification, RatingHistory
from ...base import ApplicantRepository, RatingRepository, BaseBroker

from src.tyuiu_ratings.utils import calculate_pages


class BroadcastNotificationsUseCase:
    """Рассылка уведомлений абитуриентам об их текущей ситуации в рейтинге."""
    def __init__(
            self,
            applicant_repository: ApplicantRepository,
            rating_repository: RatingRepository,
            notification_factory: NotificationFactory,
            broker: BaseBroker
    ) -> None:
        self._applicant_repository = applicant_repository
        self._rating_repository = rating_repository
        self._notification_factory = notification_factory
        self._broker = broker

    async def broadcast(self) -> None:
        async for applicants in self._iterate_applicants():
            tasks = [self._send(applicant) for applicant in applicants]
            await asyncio.gather(*tasks)

    async def _iterate_applicants(self) -> AsyncGenerator[list[ApplicantReadDTO]]:
        total_count = await self._applicant_repository.count()
        pages = calculate_pages(total_count, DEFAULT_LIMIT)
        for page in range(1, pages + 1):
            applicants = await self._applicant_repository.paginate(page, DEFAULT_LIMIT)
            yield applicants

    async def _prepare_notification(self, applicant: ApplicantReadDTO) -> Optional[Notification]:
        ratings = await self._rating_repository.read(
            applicant_id=applicant.applicant_id,
            direction=applicant.direction
        )
        rating_history = RatingHistory(ratings=ratings)
        notification = await self._notification_factory.get_notification(
            applicant=applicant,
            rating_history=rating_history
        )
        return notification

    async def _send(self, applicant: ApplicantReadDTO) -> None:
        notification = await self._prepare_notification(applicant)
        await self._broker.publish(notification)
