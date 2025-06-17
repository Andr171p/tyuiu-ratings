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
from .schemas import Profile, Exam
from .models import ProfileOrm, ExamOrm
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
                .values(**profile.model_dump(exclude={"exams"}))
            )
            await self.session.execute(stmt)
            exams_data = [
                {"applicant_id": profile.applicant_id, **exam.model_dump()}
                for exam in profile.exams
            ]
            stmt = insert(ExamOrm)
            await self.session.execute(stmt, exams_data)
            await self.session.commit()
            stmt = (
                select(ProfileOrm)
                .where(ProfileOrm.applicant_id == profile.applicant_id)
                .options(selectinload(ProfileOrm.exams))
            )
            result = await self.session.execute(stmt)
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
                .options(selectinload(ProfileOrm.exams))
            )
            result = await self.session.execute(stmt)
            profile = result.scalar_one_or_none()
            return CreatedProfile.model_validate(profile) if profile else None
        except SQLAlchemyError as e:
            await self.session.rollback()
            self.logger.error(f"Error while reading profile: {e}")
            raise ProfileReadingError(f"Error while reading profile: {e}") from e

    async def update(self, user_id: UUID, **kwargs) -> Optional[CreatedProfile]:
        exams: list[Exam] = kwargs.pop("exams", None)
        try:
            stmt = (
                update(ProfileOrm)
                .where(ProfileOrm.user_id == user_id)
                .values(**kwargs)
                .returning(ProfileOrm)
            )
            result = await self.session.execute(stmt)
            profile = result.scalar_one_or_none()
            if not profile:
                return None
            if exams is not None:
                stmt = (
                    delete(ExamOrm)
                    .where(ExamOrm.applicant_id == profile.applicant_id)
                )
                await self.session.execute(stmt)
                exams_data = [
                    {"applicant_id": profile.applicant_id, **exam}
                    for exam in exams
                ]
                stmt = insert(ExamOrm)
                await self.session.execute(stmt, exams_data)
            await self.session.commit()
            stmt = (
                select(ProfileOrm)
                .where(ProfileOrm.applicant_id == profile.applicant_id)
                .options(selectinload(ProfileOrm.exams))
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
            return result.rowcount > 0
        except SQLAlchemyError as e:
            await self.session.rollback()
            self.logger.error(f"Error while deleting profile: {e}")
            raise ProfileDeletingError(f"Error while updating profile: {e}") from e

    async def get_by_applicant_id(self, applicant_id: int) -> Optional[CreatedProfile]:
        try:
            stmt = (
                select(ProfileOrm)
                .where(ProfileOrm.applicant_id == applicant_id)
            )
            result = await self.session.execute(stmt)
            profile = result.scalar_one_or_none()
            return CreatedProfile.model_validate(profile) if profile else None
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise ProfileReadingError(f"Error while reading profile: {e}") from e

    async def get_applicants(self, user_id: UUID) -> list["CreatedApplicant"]:
        from ..applicant.dto import CreatedApplicant
        from ..applicant.models import ApplicantOrm
        try:
            stmt = (
                select(ApplicantOrm)
                .join(ProfileOrm, ApplicantOrm.applicant_id == ProfileOrm.applicant_id)
                .where(ProfileOrm.user_id == user_id)
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
        from ..rating.models import RatingOrm
        try:
            stmt = (
                select(RatingOrm)
                .join(ProfileOrm, RatingOrm.applicant_id == ProfileOrm.applicant_id)
                .where(
                    ProfileOrm.user_id == user_id,
                    RatingOrm.direction == direction
                )
            )
            results = await self.session.execute(stmt)
            ratings = results.scalars().all()
            return [Rating.model_validate(rating) for rating in ratings]
        except SQLAlchemyError as e:
            await self.session.rollback()
            self.logger.error(f"Error while receiving ratings: {e}")
            raise ProfileReadingError(f"Error while receiving ratings: {e}") from e
