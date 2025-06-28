from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from .schemas import Rating
from .dto import RatingCreation
from .models import RatingOrm
from .base import RatingRepository
from .exceptions import RatingCreationError, RatingReadingError


class SQLRatingRepository(RatingRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def bulk_upsert(self, ratings: list[RatingCreation]) -> None:
        try:
            for rating in ratings:
                stmt = (
                    insert(RatingOrm)
                    .values(**rating.model_dump())
                    .on_conflict_do_update(
                        constraint="unique_rating",
                        set_=rating.model_dump()
                    )
                )
                await self.session.execute(stmt)
            await self.session.commit()
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise RatingCreationError(f"Error while creating rating: {e}") from e

    async def read(self, applicant_id: int, direction: str) -> list[Rating]:
        try:
            stmt = (
                select(RatingOrm)
                .where(
                    RatingOrm.applicant_id == applicant_id,
                    RatingOrm.direction == direction
                )
            )
            results = await self.session.execute(stmt)
            ratings = results.scalars().all()
            return [
                Rating.model_validate(rating)
                for rating in ratings
            ] if ratings else None
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise RatingReadingError(f"Error while reading history: {e}") from e
