from typing import TYPE_CHECKING

import logging

if TYPE_CHECKING:
    from ..rating.base import RatingRepository
    from ..profile.schemas import Profile

from .schemas import Applicant
from .base import ClassifierService, RecommendationService, ApplicantRepository
from .dto import (
    ApplicantUpdateEvent,
    ApplicantPredict,
    ApplicantRecommend,
    Prediction,
    Recommendation,
    PredictedRecommendation
)
from .exceptions import (
    ApplicantsCreationError,
    RecommendationError,
    PredictionError,
    DirectionsRecommendationError
)


class UpdateApplicantsUseCase:
    def __init__(
            self,
            applicant_repository: ApplicantRepository,
            rating_repository: "RatingRepository",
            classifier_service: ClassifierService
    ) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)
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
        try:
            await self._applicant_repository.bulk_create(applicants_create)
        except ApplicantsCreationError:
            return

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


class RecommendDirectionsUseCase:
    def __init__(
            self,
            classifier_service: ClassifierService,
            recommendation_service: RecommendationService,
            applicant_repository: ApplicantRepository
    ) -> None:
        self._classifier_service = classifier_service
        self._recommendation_service = recommendation_service
        self._applicant_repository = applicant_repository

    async def __call__(self, applicant_id: int, top_n: int) -> list[PredictedRecommendation]:
        profile = await self._applicant_repository.get_profile(applicant_id)
        recommendations = await self._get_recommendations(profile, top_n)
        if not recommendations:
            raise DirectionsRecommendationError("Error while receiving recommendations")
        predicted_recommendations = await self._predict_recommendations(recommendations, points=profile.points)
        if not predicted_recommendations:
            raise DirectionsRecommendationError("Error while predict recommendations")
        marked_recommendations = await self._mark_recommendations(applicant_id, predicted_recommendations)
        return marked_recommendations

    async def _get_recommendations(self, profile: "Profile", top_n: int) -> list[Recommendation]:
        applicant_recommend = ApplicantRecommend(
            gender=profile.gender,
            points=profile.points,
            gpa=profile.gpa,
            exams=profile.exams
        )
        try:
            recommendations = await self._recommendation_service.recommend(applicant_recommend, top_n)
            return recommendations
        except RecommendationError:
            return []

    async def _predict_recommendations(
            self,
            recommendations: list[Recommendation],
            points: int
    ) -> list[PredictedRecommendation]:
        applicants_predict = [
            ApplicantPredict(points=points, direction=recommendation.direction)
            for recommendation in recommendations
        ]
        try:
            predictions = await self._classifier_service.predict_batch(applicants_predict)
        except PredictionError:
            return []
        predicted_recommendations = [
            PredictedRecommendation(
                direction_id=recommendation.direction_id,
                direction=recommendation.direction,
                probability=prediction.probability
            )
            for recommendation, prediction in zip(recommendations, predictions)
        ]
        return predicted_recommendations

    async def _mark_recommendations(
            self,
            applicant_id: int,
            predicted_recommendations: list[PredictedRecommendation]
    ) -> list[PredictedRecommendation]:
        applicants = await self._applicant_repository.read(applicant_id)
        probabilities = [applicant.probability for applicant in applicants]
        directions = [applicant.direction for applicant in applicants]
        min_probability, max_probability = min(probabilities), max(probabilities)
        marked_recommendations: list[PredictedRecommendation] = []
        for predicted_recommendation in predicted_recommendations:
            if predicted_recommendation.direction in directions:
                continue
            probability = predicted_recommendation.probability
            if min_probability <= probability < max_probability:
                predicted_recommendation.status = "SAME"
            elif probability >= max_probability:
                predicted_recommendation.status = "BETTER"
            else:
                predicted_recommendation.status = "LESS"
            marked_recommendations.append(predicted_recommendation)
        return marked_recommendations
