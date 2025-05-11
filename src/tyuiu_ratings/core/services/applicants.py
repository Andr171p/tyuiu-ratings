from typing import List

from ..entities import Applicant
from ..dto import ApplicantPredictDTO, ApplicantCreateDTO
from ..interfaces import BinaryClassifier, ApplicantRepository


class ApplicantHandler:
    def __init__(
            self,
            classifier: BinaryClassifier,
            applicant_repository: ApplicantRepository
    ) -> None:
        self._classifier = classifier
        self._applicant_repository = applicant_repository

    async def handle(self, applicants: List[Applicant]) -> ...:
        applicants_predict_dto = [
            ApplicantPredictDTO(points=applicant.points, direction=applicant.direction)
            for applicant in applicants
        ]
        probabilities = await self._classifier.predict_batch(applicants_predict_dto)
        applicants_create_dto = [
            ApplicantCreateDTO(
                applicant_id=applicant.applicant_id,
                institute=applicant.institute,
                direction=applicant.direction,
                priority=applicant.priority,
                points=applicant.points,
                bonus_points=applicant.bonus_points,
                original=applicant.original,
                probability=probability
            )
            for applicant, probability in zip(applicants, probabilities)
        ]
        await self._applicant_repository.bulk_create(applicants_create_dto)
