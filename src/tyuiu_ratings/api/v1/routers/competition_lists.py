from typing import Annotated

from uuid import UUID

from fastapi import APIRouter, status, Query, HTTPException

from dishka.integrations.fastapi import DishkaRoute, FromDishka

from src.tyuiu_ratings.core.domain import CompetitionList
from src.tyuiu_ratings.core.use_cases.competition_list import GetCompetitionListUseCase


competition_lists_router = APIRouter(
    prefix="/api/v1/competition-lists",
    tags=["Competition lists"],
    route_class=DishkaRoute
)


@competition_lists_router.get(
    path="/{user_id}",
    status_code=status.HTTP_200_OK,
    response_model=CompetitionList
)
async def get_competition_list(
        user_id: UUID,
        direction: Annotated[str, Query(..., description="Направление подготовки")],
        get_competition_list_use_case: FromDishka[GetCompetitionListUseCase]
) -> CompetitionList:
    competition_list = await get_competition_list_use_case.get(user_id, direction)
    if not competition_list:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Competition list not found")
    return competition_list
