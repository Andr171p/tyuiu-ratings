from typing import Annotated

from uuid import UUID

from fastapi import APIRouter, status, Query, HTTPException

from dishka.integrations.fastapi import FromDishka, DishkaRoute

from src.tyuiu_ratings.core.dto import (
    RerankedPriorityDTO,
    PredictedRecommendationDTO,
    ApplicantRatingHistoryDTO
)
from src.tyuiu_ratings.core.use_cases.applicant import (
    RerankPrioritiesUseCase,
    RecommendDirectionsUseCase
)
from src.tyuiu_ratings.core.constants import MIN_TOP_N, MAX_TOP_N


applicants_router = APIRouter(
    prefix="/api/v1/applicants",
    tags=["Applicants"],
    route_class=DishkaRoute
)


@applicants_router.get(
    path="/{user_id}/rerank-priorities",
    status_code=status.HTTP_200_OK,
    response_model=list[RerankedPriorityDTO]
)
async def rerank_priorities(
        user_id: UUID,
        rerank_priorities_use_case: FromDishka[RerankPrioritiesUseCase]
) -> list[RerankedPriorityDTO]:
    reranked_priorities = await rerank_priorities_use_case.rerank(user_id)
    return reranked_priorities


@applicants_router.get(
    path="/{user_id}/recommend-directions",
    status_code=status.HTTP_200_OK,
    response_model=list[PredictedRecommendationDTO]
)
async def get_recommendations(
        user_id: UUID,
        top_n: Annotated[int, Query(ge=MIN_TOP_N, le=MAX_TOP_N, description="Количество рекомендаций")],
        recommend_directions_use_case: FromDishka[RecommendDirectionsUseCase]
) -> list[PredictedRecommendationDTO]:
    recommendations = await recommend_directions_use_case.recommend(user_id, top_n)
    return recommendations


@applicants_router.get(
    path="/{user_id}/rating-history",
    status_code=status.HTTP_200_OK,
    response_model=list[ApplicantRatingHistoryDTO]
)
async def get_rating_history(
        user_id: UUID,
        direction: DirectionQuery,
        rating_history_reader: FromDishka[RatingHistoryReader]
) -> list[ApplicantRatingHistoryDTO]:
    rating_histories = await rating_history_reader.read(user_id, direction)
    if not rating_histories:
        raise HTTPException(status_code=404, detail="Rating history not found")
    return rating_histories
