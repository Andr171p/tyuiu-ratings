from uuid import UUID

from fastapi import APIRouter, status, HTTPException

from dishka.integrations.fastapi import FromDishka, DishkaRoute

from src.tyuiu_ratings.core.domain import Rating
from src.tyuiu_ratings.core.dto import (
    RerankedPriorityDTO,
    PredictedRecommendationDTO,
    ApplicantRatingHistoryDTO
)
from src.tyuiu_ratings.core.use_cases import (
    PrioritiesReranker,
    RatingReader,
    DirectionRecommender,
    RatingHistoryService
)
from ..params import DirectionQuery, TopNQuery


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
        priorities_reranker: FromDishka[PrioritiesReranker]
) -> list[RerankedPriorityDTO]:
    reranked_priorities = await priorities_reranker.rerank(user_id)
    return reranked_priorities


@applicants_router.get(
    path="/{user_id}/rating",
    status_code=status.HTTP_200_OK,
    response_model=Rating
)
async def get_rating(
        user_id: UUID,
        direction: DirectionQuery,
        rating_reader: FromDishka[RatingReader]
) -> Rating:
    rating = await rating_reader.read(user_id, direction)
    if not rating:
        raise HTTPException(status_code=404, detail="Rating not found")
    return rating


@applicants_router.get(
    path="/{user_id}/recommend",
    status_code=status.HTTP_200_OK,
    response_model=list[PredictedRecommendationDTO]
)
async def get_recommendations(
        user_id: UUID,
        top_n: TopNQuery,
        direction_recommender: FromDishka[DirectionRecommender]
) -> list[PredictedRecommendationDTO]:
    recommendations = await direction_recommender.recommend(user_id, top_n)
    return recommendations


@applicants_router.get(
    path="/{user_id}/rating-history",
    status_code=status.HTTP_200_OK,
    response_model=list[ApplicantRatingHistoryDTO]
)
async def get_rating_histories(
        user_id: UUID,
        rating_history_service: FromDishka[RatingHistoryService]
) -> list[ApplicantRatingHistoryDTO]:
    rating_histories = await rating_history_service.get_rating_histories(user_id)
    if not rating_histories:
        raise HTTPException(status_code=404, detail="Rating history not found")
    return rating_histories
