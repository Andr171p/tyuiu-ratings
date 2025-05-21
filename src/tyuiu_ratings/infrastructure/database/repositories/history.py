from datetime import datetime

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import HistoryOrm
from src.tyuiu_ratings.core.domain import Rank, History
from src.tyuiu_ratings.core.interfaces import HistoryRepository


class SQLHistoryRepository(HistoryRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def bulk_create(self, places: list[Rank]) -> None:
        today = datetime.today()
        try:
            history_orms: list[HistoryOrm] = []
            for place in places:
                stmt = (
                    select(HistoryOrm)
                    .where(
                        HistoryOrm.applicant_id == place.applicant_id,
                        HistoryOrm.date == today
                    )
                )
                existing = await self.session.execute(stmt)
                if not existing:
                    history_orms.append(HistoryOrm(**place.model_dump()))
                self.session.add_all(history_orms)
                await self.session.commit()
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise RuntimeError(f"Error while creating history: {e}")

    async def read(self, applicant_id: int) -> History:
        try:
            stmt = (
                select(HistoryOrm)
                .where(HistoryOrm.applicant_id == applicant_id)
            )
            results = await self.session.execute(stmt)
            places = results.scalars().all()
            return [Rank.model_validate(place) for place in places] if places else None
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise RuntimeError(f"Error while reading history: {e}")
