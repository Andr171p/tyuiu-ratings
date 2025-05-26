from uuid import UUID

from fastapi import APIRouter, status

from dishka.integrations.fastapi import FromDishka, DishkaRoute

from src.tyuiu_ratings.core.use_cases import PrioritiesReranker
from src.tyuiu_ratings.core.interfaces import ApplicantRepository
from src.tyuiu_ratings.core.dto import ApplicantReadDTO
from ..schemas import RerankedPrioritiesResponse


applicants_router = APIRouter(
    prefix="/api/v1/applicants",
    tags=["Applicants"],
    route_class=DishkaRoute
)


@applicants_router.get(
    path="/{user_id}/rerank-priorities",
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
    path="/{user_id}/recommend",
    status_code=status.HTTP_200_OK,
    response_model=...
)
async def get_recommendations(
        user_id: UUID,
) -> ...:
    ...
