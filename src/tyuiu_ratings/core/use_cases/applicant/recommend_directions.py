from uuid import UUID

from ...domain import Profile
from ...base import (
    ApplicantRepository,
    ProfileRepository,
    ClassifierService,
    RecommendationService
)
from ...dto import (
    RecommendationDTO,
    ApplicantPredictDTO,
    ApplicantRecommendDTO,
    PredictedRecommendationDTO,
)


class RecommendDirectionsUseCase:
    """
        Сервис для рекомендации направлений подготовки шанс поступления на которые не меньше текущего

        - Учитывает реальную ситуацию
        - Размечает рекомендации по статусам
    """
    def __init__(
            self,
            applicant_repository: ApplicantRepository,
            profile_repository: ProfileRepository,
            classifier_service: ClassifierService,
            recommendation_service: RecommendationService
    ) -> None:
        self._applicant_repository = applicant_repository
        self._profile_repository = profile_repository
        self._classifier_service = classifier_service
        self._recommendation_service = recommendation_service

    async def recommend(self, user_id: UUID, top_n: int) -> list[PredictedRecommendationDTO]:
        profile = await self._profile_repository.read(user_id)
        points = await self._profile_repository.get_applicant_points(user_id)
        recommendations = await self._get_recommendations(profile, points, top_n)
        predicted_recommendations = await self._get_predictions(points, recommendations)
        filtered_recommendations = await self._filter_by_probability(
            applicant_id=profile.applicant_id,
            predicted_recommendations=predicted_recommendations
        )
        return filtered_recommendations

    async def _get_recommendations(
            self,
            profile: Profile,
            points: int,
            top_n: int
    ) -> list[RecommendationDTO]:
        applicant_dto = ApplicantRecommendDTO(
            gender=profile.gender,
            gpa=profile.gpa,
            points=points,
            exams=profile.exams
        )
        recommendations = await self._recommendation_service.recommend(applicant_dto, top_n)
        return recommendations

    async def _get_predictions(
            self,
            points: int,
            recommendations: list[RecommendationDTO]
    ) -> list[PredictedRecommendationDTO]:
        applicant_dtos = [
            ApplicantPredictDTO(points=points, direction=recommendation.direction)
            for recommendation in recommendations
        ]
        predictions = await self._classifier_service.predict_batch(applicant_dtos)
        return [
            PredictedRecommendationDTO(
                direction_id=recommendation.direction_id,
                direction=recommendation.direction,
                probability=prediction.probability
            )
            for recommendation, prediction in zip(recommendations, predictions)
        ]

    async def _filter_by_probability(
            self,
            applicant_id: int,
            predicted_recommendations: list[PredictedRecommendationDTO]
    ) -> list[PredictedRecommendationDTO]:
        """
            Фильтрует рекомендации по вероятности поступления.

            Рекомендации делятся на:
            - BETTER: вероятность выше максимальной текущей
            - SAME: в диапазоне между минимальной и максимальной
            - другие отбрасываются

            Args:
                applicant_id: ID абитуриента
                predicted_recommendations: Список рекомендаций с вероятностями для фильтрации

            Returns:
                Отфильтрованный список рекомендаций с установленными статусами
            """
        applicants = await self._applicant_repository.sort_by_priority(applicant_id)
        probabilities = [applicant.probability for applicant in applicants]
        min_probability, max_probability = min(probabilities), max(probabilities)
        filtered: list[PredictedRecommendationDTO] = []
        for predicted_recommendation in predicted_recommendations:
            probability = predicted_recommendation.probability
            if min_probability <= probability < max_probability:
                filtered.append(predicted_recommendation)
            elif probability >= max_probability:
                predicted_recommendation.status = "BETTER"
                filtered.append(predicted_recommendation)
        return filtered
