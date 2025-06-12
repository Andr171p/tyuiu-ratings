from typing import Annotated

from uuid import UUID

from fastapi import APIRouter, status, HTTPException, Query

from dishka.integrations.fastapi import DishkaRoute, FromDishka as Depends

from .schemas import Profile
from .dto import CreatedProfile, ProfileRefactoring
from .base import ProfileRepository
from .exceptions import (
    ProfileCreationError,
    ProfileReadingError,
    ProfileUpdatingError,
    ProfileDeletingError
)
from ..applicant.dto import CreatedApplicant
from ..rating.schemas import Rating


profiles_router = APIRouter(
    prefix="/api/v1/profiles",
    tags=["Profiles"],
    route_class=DishkaRoute
)


@profiles_router.post(
    path="",
    status_code=status.HTTP_201_CREATED,
    response_model=CreatedProfile,
    summary="Создаёт профиль абитуриента",
)
async def create_profile(
        profile: Profile,
        profile_repository: Depends[ProfileRepository]
) -> CreatedProfile:
    try:
        created_profile = await profile_repository.create(profile)
        return created_profile
    except ProfileCreationError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error while creating profile"
        )


@profiles_router.get(
    path="/{user_id}",
    status_code=status.HTTP_200_OK,
    response_model=CreatedProfile,
    summary="Возвращает профиль абитуриента по его ID полученному при регистрации"
)
async def get_profile(
        user_id: UUID,
        profile_repository: Depends[ProfileRepository]
) -> CreatedProfile:
    try:
        profile = await profile_repository.read(user_id)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found"
            )
        return profile
    except ProfileReadingError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error while receiving profile"
        )


@profiles_router.patch(
    path="/{user_id}",
    status_code=status.HTTP_200_OK,
    response_model=CreatedProfile,
    summary="Обновляет профиль абитуриента. Подходит для редактирования профиля"
)
async def update_profile(
        user_id: UUID,
        profile: ProfileRefactoring,
        profile_repository: Depends[ProfileRepository]
) -> CreatedProfile:
    try:
        updated_profile = await profile_repository.update(
            user_id,
            **profile.model_dump(exclude_none=True)
        )
        if not updated_profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found"
            )
        return updated_profile
    except ProfileUpdatingError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error while updating profile"
        )


@profiles_router.delete(
    path="/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удаляет профиль абитуриента"
)
async def delete_profile(
        user_id: UUID,
        profile_repository: Depends[ProfileRepository]
) -> None:
    try:
        is_deleted = await profile_repository.delete(user_id)
        if not is_deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found"
            )
        return
    except ProfileDeletingError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error while deleting profile"
        )


@profiles_router.get(
    path="/{user_id}/applicants",
    status_code=status.HTTP_200_OK,
    response_model=list[CreatedApplicant],
    summary="Возвращает все направления с детальной информацией на которые абитуриент подал документы"
)
async def get_applicants(
        user_id: UUID,
        profile_repository: Depends[ProfileRepository]
) -> list[CreatedApplicant]:
    try:
        applicants = await profile_repository.get_applicants(user_id)
        return applicants
    except ProfileReadingError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error while receiving applicants"
        )


@profiles_router.get(
    path="/{user_id}/rating-history",
    status_code=status.HTTP_200_OK,
    response_model=list[Rating],
    summary=""""Возвращает историю изменения рейтинга 
    на конкретное направление подготовки с списках за каждый день"""
)
async def get_rating_history(
        user_id: UUID,
        direction: Annotated[str, Query(..., description="Направление подготовки")],
        profile_repository: Depends[ProfileRepository]
) -> list[Rating]:
    try:
        ratings = await profile_repository.get_ratings(user_id, direction)
        return ratings
    except ProfileReadingError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error while receiving rating history"
        )
