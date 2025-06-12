from abc import ABC, abstractmethod

from .schemas import Rating
from .dto import RatingCreation


class RatingRepository(ABC):
    @abstractmethod
    async def bulk_create(self, ratings: list[RatingCreation]) -> None: pass

    @abstractmethod
    async def read(self, applicant_id: int, direction: str) -> list[Rating]: pass
