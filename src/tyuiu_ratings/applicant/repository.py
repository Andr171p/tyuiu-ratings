from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..profile.schemas import Profile

from sqlalchemy import select, func
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from .models import ApplicantOrm
from .base import ApplicantRepository
from .dto import CreatedApplicant, ApplicantCreate
from .exceptions import ApplicantsCreationError, ApplicantsReadingError


class SQLApplicantRepository(ApplicantRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def bulk_upsert(self, applicants: list[ApplicantCreate]) -> None:
        try:
            for applicant in applicants:
                stmt = (
                    insert(ApplicantOrm)
                    .values(**applicant.model_dump())
                    .on_conflict_do_update(
                        constraint="unique_applicant_direction",
                        set_=applicant.model_dump()
                    )
                )
                await self.session.execute(stmt)
            await self.session.commit()
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise ApplicantsCreationError(f"Error while bulk creating: {e}") from e

    async def read(self, applicant_id: int) -> list[CreatedApplicant]:
        try:
            stmt = (
                select(ApplicantOrm)
                .where(ApplicantOrm.applicant_id == applicant_id)
                .order_by(ApplicantOrm.priority.desc())
            )
            results = await self.session.execute(stmt)
            applicants = results.scalars().all()
            return [CreatedApplicant.model_validate(applicant) for applicant in applicants]
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise ApplicantsReadingError(f"Error while reading by applicant id: {e}") from e

    async def get_profile(self, applicant_id: int) -> Optional["Profile"]:
        from ..profile.models import ProfileOrm
        from ..profile.schemas import Profile
        try:
            stmt = (
                select(ProfileOrm)
                .where(ProfileOrm.applicant_id == applicant_id)
                .options(selectinload(ProfileOrm.exams))
            )
            result = await self.session.execute(stmt)
            profile = result.scalars().first()
            return Profile.model_validate(profile) if profile else None
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise ApplicantsReadingError(f"Error while reading profile: {e}") from e

    async def get_applicant(self, applicant_id: int, direction: str) -> Optional[CreatedApplicant]:
        try:
            stmt = (
                select(ApplicantOrm)
                .where(
                    ApplicantOrm.applicant_id == applicant_id,
                    ApplicantOrm.direction == direction
                )
            )
            result = await self.session.execute(stmt)
            applicant = result.scalar_one_or_none()
            return CreatedApplicant.model_validate(applicant) if applicant else None
        except SQLAlchemyError as e:
            await self.session.commit()
            raise ApplicantsReadingError(f"Error while reading applicant: {e}") from e

    async def get_applicants_by_direction(self, direction: str) -> list[CreatedApplicant]:
        try:
            stmt = (
                select(ApplicantOrm)
                .where(ApplicantOrm.direction == direction)
                .order_by(ApplicantOrm.rank.desc())
            )
            results = await self.session.execute(stmt)
            applicants = results.scalars().all()
            return [CreatedApplicant.model_validate(applicant) for applicant in applicants]
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise ApplicantsReadingError(f"Error while reading by direction: {e}") from e

    async def paginate(self, page: int, limit: int) -> list[CreatedApplicant]:
        try:
            offset = (page - 1) * limit
            stmt = (
                select(ApplicantOrm)
                .offset(offset)
                .limit(limit)
            )
            results = await self.session.execute(stmt)
            applicants = results.scalars().all()
            return [CreatedApplicant.model_validate(applicant) for applicant in applicants]
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise ApplicantsReadingError(f"Error while paginating applicants: {e}") from e

    async def paginate_by_direction(
            self,
            direction: str,
            page: int,
            limit: int
    ) -> list[CreatedApplicant]:
        try:
            offset = (page - 1) * limit
            stmt = (
                select(ApplicantOrm)
                .where(ApplicantOrm.direction == direction)
                .offset(offset)
                .limit(limit)
            )
            results = await self.session.execute(stmt)
            applicants = results.scalars().all()
            return [CreatedApplicant.model_validate(applicant) for applicant in applicants]
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise ApplicantsReadingError(f"Error while paginate by direction: {e}") from e

    async def sort_by_probability(self, applicant_id: int) -> list[CreatedApplicant]:
        try:
            stmt = (
                select(ApplicantOrm)
                .where(ApplicantOrm.applicant_id == applicant_id)
                .order_by(ApplicantOrm.probability.desc())
            )
            results = await self.session.execute(stmt)
            applicants = results.scalars().all()
            return [CreatedApplicant.model_validate(applicant) for applicant in applicants]
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise ApplicantsReadingError(f"Error while sorting by probability: {e}") from e

    async def count(self) -> int:
        try:
            stmt = (
                select(func.count)
                .select_from(ApplicantOrm)
            )
            count = await self.session.execute(stmt)
            return count.scalar()
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise ApplicantsReadingError(f"Error while reading count: {e}") from e
