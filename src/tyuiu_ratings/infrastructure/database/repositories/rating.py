from datetime import datetime

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import RatingOrm
from src.tyuiu_ratings.core.domain import Rating
from src.tyuiu_ratings.core.base import RatingRepository


class SQLRatingRepository(RatingRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def bulk_create(self, rating_positions: list[Rating]) -> None:
        today = datetime.today()
        try:
            rating_orms: list[RatingOrm] = []
            for rating_position in rating_positions:
                stmt = (
                    select(RatingOrm)
                    .where(
                        RatingOrm.applicant_id == rating_position.applicant_id,
                        RatingOrm.date == today
                    )
                )
                existing = await self.session.execute(stmt)
                if not existing:
                    rating_orms.append(RatingOrm(**rating_position.model_dump()))
                self.session.add_all(rating_orms)
                await self.session.commit()
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise RuntimeError(f"Error while creating history: {e}")

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
            raise RuntimeError(f"Error while reading history: {e}")
