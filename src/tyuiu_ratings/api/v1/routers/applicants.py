from uuid import UUID

from fastapi import APIRouter, status

from dishka.integrations.fastapi import FromDishka, DishkaRoute

from src.tyuiu_ratings.core.use_cases import PrioritiesReranker
from ..schemas import ApplicantsResponse


applicants_router = APIRouter(
    prefix="/api/v1/applicants",
    tags=["Applicants"],
    route_class=DishkaRoute
)


@applicants_router.get(
    path="/{user_id}/rerank-priorities",
    status_code=status.HTTP_200_OK,
    response_model=ApplicantsResponse
)
async def rerank_priorities(
        user_id: UUID,
        priorities_reranker: FromDishka[PrioritiesReranker]
) -> ApplicantsResponse:
    applicants = await priorities_reranker.rerank(user_id)
    return ApplicantsResponse(applicants=applicants)
