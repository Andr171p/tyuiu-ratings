from uuid import UUID

from .domain import Applicant
from .interfaces import AdmissionClassifier, ApplicantRepository, ProfileRepository
from .dto import ApplicantPredictDTO, ApplicantReadDTO


class RatingUpdater:
    def __init__(
            self,
            admission_classifier: AdmissionClassifier,
            applicant_repository: ApplicantRepository
    ) -> None:
        self.admission_classifier = admission_classifier
        self.applicant_repository = applicant_repository

    async def update(self, applicants: list[Applicant]) -> None:
        probabilities = await self._predict_probabilities(applicants)
        applicants_dto = [
            applicant.to_create_dto(probability)
            for applicant, probability in zip(applicants, probabilities)
        ]
        await self.applicant_repository.bulk_create(applicants_dto)

    async def _predict_probabilities(self, applicants: list[Applicant]) -> list[float]:
        applicants_dto = [
            ApplicantPredictDTO(points=applicant.points, direction=applicant.direction)
            for applicant in applicants
        ]
        probabilities = await self.admission_classifier.predict_batch(applicants_dto)
        return probabilities


class PrioritiesReranker:
    def __init__(
            self,
            applicant_repository: ApplicantRepository,
            profile_repository: ProfileRepository
    ) -> None:
        self.applicant_repository = applicant_repository
        self.profile_repository = profile_repository

    async def rerank(self, user_id: UUID) -> list[ApplicantReadDTO]:
        profile = await self.profile_repository.read(user_id)
        applicants = await self.applicant_repository.get_by_applicant_id(profile.applicant_id)
        applicants.sort(key=lambda appl: appl.probability, reverse=True)
        for priority, applicant in enumerate(applicants, start=1):
            applicant.priority = priority
        return applicants
