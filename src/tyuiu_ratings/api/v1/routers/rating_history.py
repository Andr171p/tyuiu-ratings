from typing import Annotated

from uuid import UUID

from fastapi import APIRouter, status, Query, HTTPException

from dishka.integrations.fastapi import DishkaRoute, FromDishka

from src.tyuiu_ratings.core.dto import ApplicantRatingHistoryDTO
from src.tyuiu_ratings.core.use_cases.rating_history import GetRatingHistoryUseCase


rating_history_router = APIRouter(
    prefix="/api/v1/rating-history",
    tags=["Rating history"],
    route_class=DishkaRoute
)


@rating_history_router.get(
    path="/{user_id}",
    status_code=status.HTTP_200_OK,
    response_model=ApplicantRatingHistoryDTO
)
async def get_rating_history(
        user_id: UUID,
        direction: Annotated[str, Query(..., description="Направление подготовки")],
        get_rating_history_use_case: FromDishka[GetRatingHistoryUseCase]
) -> ApplicantRatingHistoryDTO:
    applicant_rating_history = await get_rating_history_use_case.get(user_id, direction)
    if not applicant_rating_history:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rating history not found")
    return applicant_rating_history
