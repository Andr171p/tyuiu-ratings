from typing import List, Optional

from sqlalchemy import select, func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert

from ..models import ApplicantOrm
from src.tyuiu_ratings.core.interfaces import ApplicantRepository
from src.tyuiu_ratings.core.dto import ApplicantReadDTO, ApplicantCreateDTO


class SQLApplicantRepository(ApplicantRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, applicant: ApplicantCreateDTO) -> None:
        try:
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
            raise RuntimeError(f"Error while creating: {e}")

    async def bulk_create(self, applicants: List[ApplicantCreateDTO]) -> None:
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
            raise RuntimeError(f"Error while bulk creating: {e}")

    async def read(self, applicant_id: int) -> Optional[ApplicantReadDTO]:
        try:
            stmt = (
                select(ApplicantOrm)
                .where(ApplicantOrm.applicant_id == applicant_id)
            )
            result = await self.session.execute(stmt)
            applicant = result.scalar_one_or_none()
            return ApplicantReadDTO.model_validate(applicant) if applicant else None
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise RuntimeError(f"Error while reading {e}")

    async def get_by_direction(self, direction: str) -> List[ApplicantReadDTO]:
        try:
            stmt = (
                select(ApplicantOrm)
                .where(ApplicantOrm.direction == direction)
            )
            results = await self.session.execute(stmt)
            applicants = results.scalars().all()
            return [ApplicantReadDTO.model_validate(applicant) for applicant in applicants]
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise RuntimeError(f"Error while reading by direction: {e}")

    async def get_by_applicant_id(self, applicant_id: int) -> list[ApplicantReadDTO]:
        try:
            stmt = (
                select(ApplicantOrm)
                .where(ApplicantOrm.applicant_id == applicant_id)
            )
            results = await self.session.execute(stmt)
            applicants = results.scalars().all()
            return [ApplicantReadDTO.model_validate(applicant) for applicant in applicants]
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise RuntimeError(f"Error while reading by applicant id: {e}")

    async def paginate(self, page: int, limit: int) -> list[ApplicantReadDTO]:
        try:
            offset = (page - 1) * limit
            stmt = (
                select(ApplicantOrm)
                .offset(offset)
                .limit(limit)
            )
            results = await self.session.execute(stmt)
            applicants = results.scalars().all()
            return [ApplicantReadDTO.model_validate(applicant) for applicant in applicants]
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise RuntimeError(f"Error while paginating applicants: {e}")

    async def paginate_by_direction(
            self,
            direction: str,
            page: int,
            limit: int
    ) -> List[ApplicantReadDTO]:
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
            return [ApplicantReadDTO.model_validate(applicant) for applicant in applicants]
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise RuntimeError(f"Error while paginate by direction: {e}")

    async def sort_by_probability(self, applicant_id: int) -> list[ApplicantReadDTO]:
        try:
            stmt = (
                select(ApplicantOrm)
                .where(ApplicantOrm.applicant_id == applicant_id)
                .order_by(ApplicantOrm.probability.desc())
            )
            results = await self.session.execute(stmt)
            applicants = results.scalars().all()
            return [ApplicantReadDTO.model_validate(applicant) for applicant in applicants]
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
