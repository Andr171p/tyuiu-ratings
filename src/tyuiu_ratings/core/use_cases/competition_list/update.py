from datetime import datetime

from ...domain import Applicant
from ...dto import PredictionDTO, ApplicantPredictDTO, RatingCreateDTO
from ...base import ClassifierService, ApplicantRepository, RatingRepository


class UpdateCompetitionListUseCase:
    """Обновление конкурсных списков и истории рейтинга."""
    def __init__(
            self,
            classifier_service: ClassifierService,
            applicant_repository: ApplicantRepository,
            rating_repository: RatingRepository
    ) -> None:
        self._classifier_service = classifier_service
        self._applicant_repository = applicant_repository
        self._rating_repository = rating_repository

    async def update(self, applicants: list[Applicant]) -> None:
        predictions = await self._get_predictions(applicants)
        await self._update_applicants(applicants, predictions)
        await self._update_ratings(applicants)

    async def _get_predictions(self, applicants: list[Applicant]) -> list[PredictionDTO]:
        """Рассчитывает вероятность поступления на бюджет для каждого абитуриента."""
        applicant_dtos = [
            ApplicantPredictDTO(
                points=applicant.points,
                direction=applicant.direction
            )
            for applicant in applicants
        ]
        predictions = await self._classifier_service.predict_batch(applicant_dtos)
        return predictions

    async def _update_applicants(
            self,
            applicants: list[Applicant],
            predictions: list[PredictionDTO]
    ) -> None:
        """Обновляет списки абитуриентов с рассчитанными вероятностями."""
        applicants_dto = [
            applicant.to_create_dto(prediction.probability)
            for applicant, prediction in zip(applicants, predictions)
        ]
        await self._applicant_repository.bulk_create(applicants_dto)

    async def _update_ratings(self, applicants: list[Applicant]) -> None:
        """Обновляет историю рейтинга абитуриента."""
        await self._rating_repository.bulk_create([
            RatingCreateDTO(
                applicant_id=applicant.applicant_id,
                rank=applicant.rank,
                date=datetime.today()
            )
            for applicant in applicants
        ])
