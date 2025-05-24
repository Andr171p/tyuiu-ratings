from datetime import datetime

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import RatingPositionOrm
from src.tyuiu_ratings.core.domain import RatingPosition
from src.tyuiu_ratings.core.interfaces import HistoryRepository


class SQLHistoryRepository(HistoryRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def bulk_create(self, rating_positions: list[RatingPosition]) -> None:
        today = datetime.today()
        try:
            rating_position_orms: list[RatingPositionOrm] = []
            for rating_position in rating_positions:
                stmt = (
                    select(RatingPositionOrm)
                    .where(
                        RatingPositionOrm.applicant_id == rating_position.applicant_id,
                        RatingPositionOrm.date == today
                    )
                )
                existing = await self.session.execute(stmt)
                if not existing:
                    rating_position_orms.append(RatingPositionOrm(**rating_position.model_dump()))
                self.session.add_all(rating_position_orms)
                await self.session.commit()
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise RuntimeError(f"Error while creating history: {e}")

    async def read(self, applicant_id: int, direction: str) -> list[RatingPosition]:
        try:
            stmt = (
                select(RatingPositionOrm)
                .where(
                    RatingPositionOrm.applicant_id == applicant_id,
                    RatingPositionOrm.direction == direction
                )
            )
            results = await self.session.execute(stmt)
            rating_positions = results.scalars().all()
            return [
                RatingPosition.model_validate(rating_position)
                for rating_position in rating_positions
            ] if rating_positions else None
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise RuntimeError(f"Error while reading history: {e}")
