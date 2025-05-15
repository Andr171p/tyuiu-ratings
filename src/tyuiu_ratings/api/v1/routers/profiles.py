from uuid import UUID

from fastapi import APIRouter, status, HTTPException

from dishka.integrations.fastapi import FromDishka, DishkaRoute

from src.tyuiu_ratings.core.entities import Profile
from src.tyuiu_ratings.core.dto import ProfileReadDTO
from src.tyuiu_ratings.core.interfaces import ProfileRepository


profiles_router = APIRouter(
    prefix="/api/v1/profiles",
    tags=["Profiles"],
    route_class=DishkaRoute
)


@profiles_router.post(
    path="/",
    status_code=status.HTTP_201_CREATED,
    response_model=ProfileReadDTO
)
async def create_profile(
        profile: Profile,
        profile_repository: FromDishka[ProfileRepository]
) -> ProfileReadDTO:
    return await profile_repository.create(profile)


@profiles_router.get(
    path="/{user_id}",
    status_code=status.HTTP_200_OK,
    response_model=ProfileReadDTO
)
async def get_profile(
        user_id: UUID,
        profile_repository: FromDishka[ProfileRepository]
) -> ProfileReadDTO:
    profile = await profile_repository.read(user_id)
    if not profile:
        raise HTTPException(status_code=404, detail=f"Profile not found")
    return profile


@profiles_router.put(
    path="/",
    status_code=status.HTTP_200_OK,
    response_model=ProfileReadDTO
)
async def update_profile(
        profile: Profile,
        profile_repository: FromDishka[ProfileRepository]
) -> ProfileReadDTO:
    updated_profile = await profile_repository.update(profile)
    if not updated_profile:
        raise HTTPException(status_code=404, detail=f"Profile doesn't exist")
    return updated_profile


@profiles_router.delete(
    path="/{user_id}",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=ProfileReadDTO
)
async def delete_profile(
        user_id: UUID,
        profile_repository: FromDishka[ProfileRepository]
) -> ProfileReadDTO:
    deleted_profile = await profile_repository.delete(user_id)
    if not deleted_profile:
        raise HTTPException(status_code=404, detail="Profile doesn't exist")
    return deleted_profile
