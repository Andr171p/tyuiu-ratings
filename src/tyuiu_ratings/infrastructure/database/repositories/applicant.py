from typing import List, Optional

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import ApplicantOrm
from src.tyuiu_ratings.core.interfaces import ApplicantRepository
from src.tyuiu_ratings.core.entities.admission import Applicant
from src.tyuiu_ratings.core.dto import ApplicantReadDTO


class SQLApplicantRepository(ApplicantRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, applicant: Applicant) -> None:
        try:
            applicant_orm = ApplicantOrm(**applicant.model_dump())
            self.session.add(applicant_orm)
            await self.session.commit()
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise RuntimeError(f"Error while creating: {e}")

    async def bulk_create(self, applicants: List[Applicant]) -> None:
        try:
            for applicant in applicants:
                applicant_orm = ApplicantOrm(**applicant.model_dump())
                self.session.add(applicant_orm)
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
            return Applicant.model_validate(applicant) if applicant else None
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise RuntimeError(f"Error while reading {e}")

    async def update(self, applicant: Applicant) -> None:
        try:
            stmt = (
                update(ApplicantOrm)
                .where(ApplicantOrm.applicant_id == applicant.applicant_id)
                .values(**applicant.model_dump())
            )
            await self.session.execute(stmt)
            await self.session.commit()
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise RuntimeError(f"Error while updating: {e}")

    async def bulk_update(self, applicants: List[Applicant]) -> None:
        try:
            for applicant in applicants:
                stmt = (
                    update(ApplicantOrm)
                    .where(ApplicantOrm.applicant_id == applicant.applicant_id)
                    .values(**applicant.model_dump())
                )
                await self.session.execute(stmt)
            await self.session.commit()
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise RuntimeError(f"Error while bulk updating: {e}")

    async def delete(self, applicant_id: int) -> int:
        try:
            stmt = (
                delete(ApplicantOrm)
                .where(ApplicantOrm.applicant_id == applicant_id)
                .returning(ApplicantOrm.applicant_id)
            )
            applicant_id = await self.session.execute(stmt)
            return applicant_id.scalar()
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise RuntimeError(f"Error while deleting: {e}")

    async def get_by_direction(self, direction: str) -> List[Applicant]:
        try:
            stmt = (
                select(ApplicantOrm)
                .where(ApplicantOrm.direction == direction)
            )
            results = await self.session.execute(stmt)
            applicants = results.scalars().all()
            return [Applicant.model_validate(applicant) for applicant in applicants]
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise RuntimeError(f"Error while reading by direction: {e}")

    async def paginate_by_direction(
            self,
            direction: str,
            page: int,
            limit: int
    ) -> List[Applicant]:
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
            return [Applicant.model_validate(applicant) for applicant in applicants]
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise RuntimeError(f"Error while paginate by direction: {e}")
