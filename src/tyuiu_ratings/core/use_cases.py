from collections.abc import AsyncGenerator

import asyncio
from uuid import UUID
from datetime import datetime

from .domain import Applicant, RatingPosition, RatingHistory
from .dto import ApplicantPredictDTO, ApplicantReadDTO
from ..utils import calculate_pages
from .interfaces import (
    AdmissionClassifier,
    ApplicantRepository,
    ProfileRepository,
    HistoryRepository,
    AMQPBroker,
    RecommendationSystem,
)
from ..constants import (
    DEFAULT_LIMIT,
    THRESHOLD_VELOCITY,
    BUDGET_PLACES_FOR_DIRECTIONS,
    WARNING_BUDGET_ZONE_THRESHOLD,
    POSITIVE_THRESHOLD_PROBABILITY,
    CRITICAL_THRESHOLD_PROBABILITY
)


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


class PrioritiesReranker:
    def __init__(
            self,
            applicant_repository: ApplicantRepository,
            profile_repository: ProfileRepository
    ) -> None:
        self._applicant_repository = applicant_repository
        self._profile_repository = profile_repository

    async def rerank(self, user_id: UUID) -> list[ApplicantReadDTO]:
        profile = await self._profile_repository.read(user_id)
        applicants = await self._applicant_repository.sort_by_probability(profile.applicant_id)
        return applicants


class NotificationBroadcaster:
    def __init__(
            self,
            applicant_repository: ApplicantRepository,
            profile_repository: ProfileRepository,
            history_repository: HistoryRepository,
            recommendation_system: RecommendationSystem,
            broker: AMQPBroker
    ) -> None:
        self._applicant_repository = applicant_repository
        self._profile_repository = profile_repository
        self._history_repository = history_repository
        self._recommendation_system = recommendation_system
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

    async def _send(self, applicant: ApplicantReadDTO) -> None:
        ...
