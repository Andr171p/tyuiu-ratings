from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..rating.base import RatingRepository

from .schemas import Applicant
from .dto import ApplicantUpdateEvent, ApplicantPredict, Prediction
from .base import ClassifierService, ApplicantRepository


class UpdateApplicantsUseCase:
    def __init__(
            self,
            applicant_repository: ApplicantRepository,
            rating_repository: RatingRepository,
            classifier_service: ClassifierService
    ) -> None:
        self._applicant_repository = applicant_repository
        self._rating_repository = rating_repository
        self._classifier_service = classifier_service

    async def __call__(self, applicants: list[ApplicantUpdateEvent]) -> None:
        predictions = await self._get_predictions(applicants)
        await self._update_applicants(applicants, predictions)
        await self._save_ratings(applicants)

    async def _get_predictions(self, applicants: list[Applicant]) -> list[Prediction]:
        applicant_predicts = [
            ApplicantPredict(
                points=applicant.points,
                direction=applicant.direction
            )
            for applicant in applicants
        ]
        predictions = await self._classifier_service.predict_batch(applicant_predicts)
        return predictions

    async def _update_applicants(
            self,
            applicants: list[Applicant],
            predictions: list[Prediction]
    ) -> None:
        applicants_create = [
            applicant.to_create_dto(prediction.probability)
            for applicant, prediction in zip(applicants, predictions)
        ]
        await self._applicant_repository.bulk_create(applicants_create)

    async def _save_ratings(self, applicants: list[Applicant]) -> None:
        from ..rating.dto import RatingCreation
        await self._rating_repository.bulk_create([
            RatingCreation(
                applicant_id=applicant.applicant_id,
                direction=applicant.direction,
                rank=applicant.rank
            )
            for applicant in applicants
        ])

