from uuid import UUID
from datetime import datetime

from .domain import Applicant, Rank, Notification
from .dto import ApplicantPredictDTO, ApplicantReadDTO
from .interfaces import (
    AdmissionClassifier,
    ApplicantRepository,
    ProfileRepository,
    HistoryRepository
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
        await self._update_history(applicants)

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

    async def _update_history(self, applicants: list[Applicant]) -> None:
        await self._history_repository.bulk_create([
            Rank(
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
        applicants = await self._applicant_repository.get_by_applicant_id(profile.applicant_id)
        applicants.sort(key=lambda appl: appl.probability, reverse=True)
        for priority, applicant in enumerate(applicants, start=1):
            applicant.priority = priority
        return applicants


class NotificationSender:
    def __init__(
            self,
            applicant_repository: ApplicantRepository,
            profile_repository: ProfileRepository,
            history_repository: HistoryRepository,
    ) -> None:
        self._applicant_repository = applicant_repository
        self._profile_repository = profile_repository
        self._history_repository = history_repository

    async def send(self) -> None:
        ...
