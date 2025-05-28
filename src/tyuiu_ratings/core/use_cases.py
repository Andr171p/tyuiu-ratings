from typing import Optional
from collections.abc import AsyncGenerator

import asyncio
from uuid import UUID
from datetime import datetime

from .dto import (
    ApplicantPredictDTO,
    ApplicantReadDTO,
    RerankedPriorityDTO,
    ApplicantRecommendDTO,
    RecommendationDTO,
    PredictionDTO,
    PredictedRecommendationDTO,
    RatingPositionCreateDTO,
    ApplicantRatingHistoryDTO
)
from .domain import (
    Applicant,
    RatingHistory,
    Notification,
    Rating,
    Profile
)
from .interfaces import (
    RecommendationService,
    ClassifierService,
    ApplicantRepository,
    ProfileRepository,
    RatingPositionRepository,
    AMQPBroker,
)
from .services import NotificationMaker, get_rating_status
from ..utils import calculate_pages, calculate_velocity
from ..constants import DEFAULT_LIMIT, AVAILABLE_DIRECTIONS


class RatingUpdater:
    def __init__(
            self,
            classifier_service: ClassifierService,
            applicant_repository: ApplicantRepository,
            rating_position_repository: RatingPositionRepository
    ) -> None:
        self._classifier_service = classifier_service
        self._applicant_repository = applicant_repository
        self._rating_position_repository = rating_position_repository

    async def update(self, applicants: list[Applicant]) -> None:
        predictions = await self._get_predictions(applicants)
        await self._update_applicants(applicants, predictions)
        await self._update_rating_history(applicants)

    async def _get_predictions(self, applicants: list[Applicant]) -> list[PredictionDTO]:
        applicant_dtos = [
            ApplicantPredictDTO(points=applicant.points, direction=applicant.direction)
            for applicant in applicants
        ]
        predictions = await self._classifier_service.predict_batch(applicant_dtos)
        return predictions

    async def _update_applicants(
            self,
            applicants: list[Applicant],
            predictions: list[PredictionDTO]
    ) -> None:
        applicants_dto = [
            applicant.to_create_dto(prediction.probability)
            for applicant, prediction in zip(applicants, predictions)
        ]
        await self._applicant_repository.bulk_create(applicants_dto)

    async def _update_rating_history(self, applicants: list[Applicant]) -> None:
        await self._rating_position_repository.bulk_create([
            RatingPositionCreateDTO(
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
            rating_position_repository: RatingPositionRepository,
            notification_maker: NotificationMaker,
            broker: AMQPBroker
    ) -> None:
        self._applicant_repository = applicant_repository
        self._rating_position_repository = rating_position_repository
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
        positions = await self._rating_position_repository.read(
            applicant_id=applicant.applicant_id,
            direction=applicant.direction
        )
        rating_history = RatingHistory(positions=positions)
        notification = await self._notification_maker.create(applicant, rating_history)
        return notification

    async def _send(self, applicant: ApplicantReadDTO) -> None:
        notification = await self._prepare_notification(applicant)
        await self._broker.publish(notification)


class DirectionRecommender:
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


class RatingHistoryService:
    def __init__(
            self,
            profile_repository: ProfileRepository,
            rating_position_repository: RatingPositionRepository
    ) -> None:
        self._profile_repository = profile_repository
        self._rating_position_repository = rating_position_repository

    async def get_rating_histories(self, user_id: UUID) -> list[Optional[ApplicantRatingHistoryDTO]]:
        applicants = await self._profile_repository.get_applicants(user_id)
        if not applicants:
            return []
        histories: list[ApplicantRatingHistoryDTO] = []
        for applicant in applicants:
            positions = await self._rating_position_repository.read(
                applicant_id=applicant.applicant_id,
                direction=applicant.direction
            )
            history_dto = ApplicantRatingHistoryDTO(
                applicant_id=applicant.applicant_id,
                direction=applicant.direction,
                last_change=int(calculate_velocity(positions)[-1]),
                status=get_rating_status(applicant, RatingHistory(positions=positions)),
                positions=positions
            )
            histories.append(history_dto)
        return histories
