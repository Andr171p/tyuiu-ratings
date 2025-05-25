from typing import Optional
from collections.abc import AsyncGenerator

import asyncio
from uuid import UUID
from datetime import datetime

from .dto import ApplicantPredictDTO, ApplicantReadDTO, RerankedPriorityDTO
from .domain import (
    Applicant,
    RatingPosition,
    RatingHistory,
    Notification,
    Rating
)
from .services import NotificationMaker
from .interfaces import (
    AdmissionClassifier,
    ApplicantRepository,
    ProfileRepository,
    HistoryRepository,
    AMQPBroker,
)
from ..utils import calculate_pages
from ..constants import DEFAULT_LIMIT, AVAILABLE_DIRECTIONS


class RatingUpdater:
    def __init__(
            self,
            admission_classifier: AdmissionClassifier,
            applicant_repository: ApplicantRepository,
            history_repository: HistoryRepository
    ) -> None:
        self._admission_classifier = admission_classifier
        self._applicant_repository = applicant_repository
        self._history_repository = history_repository

    async def update(self, applicants: list[Applicant]) -> None:
        probabilities = await self._predict_probabilities(applicants)
        await self._update_applicants(applicants, probabilities)
        await self._update_rating_history(applicants)

    async def _predict_probabilities(self, applicants: list[Applicant]) -> list[float]:
        applicants_dto = [
            ApplicantPredictDTO(points=applicant.points, direction=applicant.direction)
            for applicant in applicants
        ]
        probabilities = await self._admission_classifier.predict_batch(applicants_dto)
        return probabilities

    async def _update_applicants(
            self,
            applicants: list[Applicant],
            probabilities: list[float]
    ) -> None:
        applicants_dto = [
            applicant.to_create_dto(probability)
            for applicant, probability in zip(applicants, probabilities)
        ]
        await self._applicant_repository.bulk_create(applicants_dto)

    async def _update_rating_history(self, applicants: list[Applicant]) -> None:
        await self._history_repository.bulk_create([
            RatingPosition(
                applicant_id=applicant.applicant_id,
                rating=applicant.rating,
                date=datetime.today()
            )
            for applicant in applicants
        ])


class RatingReader:
    def __init__(
            self,
            profile_repository: ProfileRepository,
            applicant_repository: ApplicantRepository
    ) -> None:
        self._profile_repository = profile_repository
        self._applicant_repository = applicant_repository

    async def read(self, user_id: UUID, direction: AVAILABLE_DIRECTIONS) -> Optional[Rating]:
        profile = await self._profile_repository.read(user_id)
        applicants = await self._applicant_repository.get_by_direction(direction)
        return Rating(
            applicant_id=profile.applicant_id,
            institute=applicants[0].institute,
            direction=direction,
            rating=applicants
        )


class PrioritiesReranker:
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


class NotificationBroadcaster:
    def __init__(
            self,
            applicant_repository: ApplicantRepository,
            history_repository: HistoryRepository,
            notification_maker: NotificationMaker,
            broker: AMQPBroker
    ) -> None:
        self._applicant_repository = applicant_repository
        self._history_repository = history_repository
        self._notification_maker = notification_maker
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
        history = await self._history_repository.read(
            applicant_id=applicant.applicant_id,
            direction=applicant.direction
        )
        rating_history = RatingHistory(applicant_id=applicant.applicant_id, history=history)
        notification = await self._notification_maker.create(applicant, rating_history)
        return notification

    async def _send(self, applicant: ApplicantReadDTO) -> None:
        notification = await self._prepare_notification(applicant)
        await self._broker.publish(notification)
