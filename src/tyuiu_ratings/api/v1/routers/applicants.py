from uuid import UUID

from fastapi import APIRouter, status, HTTPException

from dishka.integrations.fastapi import FromDishka, DishkaRoute

from src.tyuiu_ratings.core.domain import Rating
from src.tyuiu_ratings.core.use_cases import PrioritiesReranker, RatingReader
from ..schemas import RerankedPrioritiesResponse, DirectionQuery


applicants_router = APIRouter(
    prefix="/api/v1/applicants",
    tags=["Applicants"],
    route_class=DishkaRoute
)


@applicants_router.get(
    path="/{user_id}/reranked-priorities",
    status_code=status.HTTP_200_OK,
    response_model=RerankedPrioritiesResponse
)
async def rerank_priorities(
        user_id: UUID,
        priorities_reranker: FromDishka[PrioritiesReranker]
) -> RerankedPrioritiesResponse:
    reranked_priorities = await priorities_reranker.rerank(user_id)
    return RerankedPrioritiesResponse(priorities=reranked_priorities)


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
    path="/{user_id}/recommendations",
    status_code=status.HTTP_200_OK,
    response_model=...
)
async def get_recommendations(
        user_id: UUID,
) -> ...:
    ...
