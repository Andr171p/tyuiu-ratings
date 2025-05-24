from uuid import UUID

from fastapi import APIRouter, status, HTTPException

from dishka.integrations.fastapi import FromDishka, DishkaRoute

from src.tyuiu_ratings.core.domain import Rating
from src.tyuiu_ratings.core.use_cases import RatingReader
from src.tyuiu_ratings.constants import AVAILABLE_DIRECTIONS


ratings_router = APIRouter(
    prefix="/api/v1/ratings",
    tags=["Ratings"],
    route_class=DishkaRoute
)


@ratings_router.get(
    path="/{user_id}/{direction}",
    status_code=status.HTTP_200_OK,
    response_model=Rating
)
async def get_rating(
        user_id: UUID,
        direction: AVAILABLE_DIRECTIONS,
        rating_reader: FromDishka[RatingReader]
) -> Rating:
    rating = await rating_reader.read(user_id, direction)
    if not rating:
        raise HTTPException(status_code=404, detail="Rating not found")
    return rating
