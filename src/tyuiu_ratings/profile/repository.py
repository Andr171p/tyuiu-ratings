from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..applicant.dto import CreatedApplicant
    from ..rating.schemas import Rating

import logging
from uuid import UUID

from sqlalchemy import insert, select, update, delete
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from .base import ProfileRepository
from .dto import CreatedProfile
from .schemas import Profile
from .models import ProfileOrm
from .exceptions import (
    ProfileCreationError,
    ProfileReadingError,
    ProfileUpdatingError,
    ProfileDeletingError
)


class SQLProfileRepository(ProfileRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)
        self.session = session

    async def create(self, profile: Profile) -> CreatedProfile:
        try:
            stmt = (
                insert(ProfileOrm)
                .values(**profile.model_dump())
                .returning(ProfileOrm)
            )
            result = await self.session.execute(stmt)
            await self.session.commit()
            created_profile = result.scalar_one()
            return CreatedProfile.model_validate(created_profile)
        except SQLAlchemyError as e:
            await self.session.rollback()
            self.logger.error(f"Error while creating profile: {e}")
            raise ProfileCreationError(f"Error while creating profile: {e}") from e

    async def read(self, user_id: UUID) -> Optional[CreatedProfile]:
        try:
            stmt = (
                select(ProfileOrm)
                .where(ProfileOrm.user_id == user_id)
            )
            result = await self.session.execute(stmt)
            profile = result.scalar_one_or_none()
            return CreatedProfile.model_validate(profile) if profile else None
        except SQLAlchemyError as e:
            await self.session.rollback()
            self.logger.error(f"Error while reading profile: {e}")
            raise ProfileReadingError(f"Error while reading profile: {e}") from e

    async def update(self, user_id: UUID, **kwargs) -> Optional[CreatedProfile]:
        try:
            stmt = (
                update(ProfileOrm)
                .where(ProfileOrm.user_id == user_id)
                .values(**kwargs)
                .returning(ProfileOrm)
            )
            result = await self.session.execute(stmt)
            profile = result.scalar_one_or_none()
            return CreatedProfile.model_validate(profile) if profile else None
        except SQLAlchemyError as e:
            await self.session.rollback()
            self.logger.error(f"Error while updating profile: {e}")
            raise ProfileUpdatingError(f"Error while updating profile: {e}") from e

    async def delete(self, user_id: UUID) -> bool:
        try:
            stmt = (
                delete(ProfileOrm)
                .where(ProfileOrm.user_id == user_id)
            )
            result = await self.session.execute(stmt)
            await self.session.commit()
            return result.rowcount() > 0
        except SQLAlchemyError as e:
            await self.session.rollback()
            self.logger.error(f"Error while deleting profile: {e}")
            raise ProfileDeletingError(f"Error while updating profile: {e}") from e

    async def get_applicants(self, user_id: UUID) -> list["CreatedApplicant"]:
        from ..applicant.dto import CreatedApplicant
        try:
            stmt = (
                select(ProfileOrm.applicants)
                .where(ProfileOrm.user_id == user_id)
                .options(
                    selectinload(ProfileOrm.applicants)
                )
            )
            results = await self.session.execute(stmt)
            applicants = results.scalars().all()
            return [CreatedApplicant.model_validate(applicant) for applicant in applicants]
        except SQLAlchemyError as e:
            await self.session.rollback()
            self.logger.error(f"Error while reading applicants: {e}")
            raise ProfileReadingError(f"Error while reading applicants: {e}") from e

    async def get_ratings(self, user_id: UUID, direction: str) -> list["Rating"]:
        from ..rating.schemas import Rating
        try:
            stmt = (
                select(ProfileOrm.ratings)
                .where(ProfileOrm.user_id == user_id)
                .options(
                    selectinload(ProfileOrm.ratings)
                )
            )
            results = await self.session.execute(stmt)
            ratings = results.scalars().all()
            return [Rating.model_validate(rating) for rating in ratings]
        except SQLAlchemyError as e:
            await self.session.rollback()
            self.logger.error(f"Error while receiving ratings: {e}")
            raise ProfileReadingError(f"Error while receiving ratings: {e}") from e
