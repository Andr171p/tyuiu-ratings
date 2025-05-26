from typing import Optional

from uuid import UUID

from sqlalchemy.orm import selectinload
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import ProfileOrm
from src.tyuiu_ratings.core.domain import Profile
from src.tyuiu_ratings.core.dto import ProfileReadDTO, ApplicantReadDTO
from src.tyuiu_ratings.core.interfaces import ProfileRepository


class SQLProfileRepository(ProfileRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, profile: Profile) -> ProfileReadDTO:
        try:
            profile_orm = ProfileOrm(**profile.model_dump())
            self.session.add(profile_orm)
            await self.session.flush()
            await self.session.commit()
            return ProfileReadDTO.model_validate(profile_orm)
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise RuntimeError(f"Error while creating profile: {e}")

    async def read(self, user_id: UUID) -> Optional[Profile]:
        try:
            stmt = (
                select(ProfileOrm)
                .where(ProfileOrm.user_id == user_id)
            )
            result = await self.session.execute(stmt)
            profile = result.scalar_one_or_none()
            return ProfileReadDTO.model_validate(profile) if profile else None
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise RuntimeError(f"Error while reding profile: {e}")

    async def update(self, profile: Profile) -> Optional[Profile]:
        try:
            stmt = (
                update(ProfileOrm)
                .where(ProfileOrm.user_id == profile.user_id)
                .values(**profile.model_dump())
                .returning(ProfileOrm)
            )
            result = await self.session.execute(stmt)
            profile = result.scalar_one_or_none()
            return ProfileReadDTO.model_validate(profile) if profile else None
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise RuntimeError(f"Error while updating profile: {e}")

    async def delete(self, user_id: UUID) -> Optional[Profile]:
        try:
            stmt = (
                delete(ProfileOrm)
                .where(ProfileOrm.user_id == user_id)
                .returning(ProfileOrm)
            )
            result = await self.session.execute(stmt)
            profile = result.scalar_one_or_none()
            return ProfileReadDTO.model_validate(profile) if profile else None
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise RuntimeError(f"Error while deleting profile: {e}")

    async def get_by_applicant_id(self, applicant_id: int) -> Optional[Profile]:
        try:
            stmt = (
                select(ProfileOrm)
                .where(ProfileOrm.applicant_id == applicant_id)
            )
            result = await self.session.execute(stmt)
            profile = result.scalar_one_or_none()
            return ProfileReadDTO.model_validate(profile) if profile else None
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise RuntimeError(f"Error while reading by applicant_id: {e}")

    async def get_applicants(self, user_id: UUID) -> list[Optional[ApplicantReadDTO]]:
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
            return [ApplicantReadDTO.model_validate(applicant) for applicant in applicants]
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise RuntimeError(f"Error while reading applicants: {e}")
