from typing import Protocol, Optional
from collections.abc import AsyncIterator

import asyncio

from pydantic import BaseModel

from .schemas import Notification
from .factory import NotificationFactory

from ..applicant.base import ApplicantRepository
from ..applicant.dto import CreatedApplicant
from ..profile.base import ProfileRepository
from ..rating.base import RatingRepository

from ..utils import calculate_pages
from ..constants import DEFAULT_LIMIT, NOTIFICATIONS_QUEUE


class BaseBroker(Protocol):
    async def publish(
            self,
            messages: BaseModel | list[BaseModel] | dict | list[dict],
            queue: str
    ) -> None: pass


class BroadcastNotificationsUseCase:
    def __init__(
            self,
            applicant_repository: ApplicantRepository,
            rating_repository: RatingRepository,
            profile_repository: ProfileRepository,
            broker: BaseBroker
    ) -> None:
        self._applicant_repository = applicant_repository
        self._rating_repository = rating_repository
        self._notification_factory = NotificationFactory(profile_repository)
        self._broker = broker

    async def __call__(self) -> None:
        async for applicants in self._iterate_applicants():
            tasks = [self._send(applicant) for applicant in applicants]
            await asyncio.gather(*tasks)

    async def _iterate_applicants(self) -> AsyncIterator[list[CreatedApplicant]]:
        total_count = await self._applicant_repository.count()
        pages = calculate_pages(total_count, DEFAULT_LIMIT)
        for page in range(1, pages + 1):
            applicants = await self._applicant_repository.paginate(page, DEFAULT_LIMIT)
            yield applicants

    async def _prepare_notification(self, applicant: CreatedApplicant) -> Optional[Notification]:
        ratings = await self._rating_repository.read(
            applicant_id=applicant.applicant_id,
            direction=applicant.direction
        )
        notification = await self._notification_factory.create_notification(
            applicant=applicant,
            ratings=ratings
        )
        return notification

    async def _send(self, applicant: CreatedApplicant) -> None:
        notification = await self._prepare_notification(applicant)
        await self._broker.publish(notification, queue=NOTIFICATIONS_QUEUE)
