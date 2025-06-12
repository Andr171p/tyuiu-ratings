from sqlalchemy import select, func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert

from .models import ApplicantOrm
from .base import ApplicantRepository
from .dto import CreatedApplicant, ApplicantCreate
from .exceptions import ApplicantsCreationError


class SQLApplicantRepository(ApplicantRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def bulk_create(self, applicants: list[ApplicantCreate]) -> None:
        try:
            for applicant in applicants:
                stmt = (
                    insert(ApplicantOrm)
                    .values(**applicant.model_dump())
                    .on_conflict_do_update(
                        index_elements=["applicant_id"],
                        set_=dict(applicant.model_dump())
                    )
                )
                await self.session.execute(stmt)
            await self.session.commit()
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise ApplicantsCreationError(f"Error while bulk creating: {e}")

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
            raise RuntimeError(f"Error while reading by applicant id: {e}")

    async def get_by_direction(self, direction: str) -> list[CreatedApplicant]:
        try:
            stmt = (
                select(ApplicantOrm)
                .where(ApplicantOrm.direction == direction)
            )
            results = await self.session.execute(stmt)
            applicants = results.scalars().all()
            return [CreatedApplicant.model_validate(applicant) for applicant in applicants]
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise RuntimeError(f"Error while reading by direction: {e}")

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
            raise RuntimeError(f"Error while paginating applicants: {e}")

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
            raise RuntimeError(f"Error while paginate by direction: {e}")

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
            raise RuntimeError(f"Error while sorting by probability: {e}")

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
            raise RuntimeError(f"Error while reading count: {e}")
