from typing import Optional, Protocol

from abc import ABC, abstractmethod

from uuid import UUID

from pydantic import BaseModel

from .domain import (
    Profile,
    Rating,
    RatingHistory,
    Notification
)
from .dto import (
    ProfileReadDTO,
    ApplicantReadDTO,
    ApplicantCreateDTO,
    ApplicantPredictDTO,
    ApplicantRecommendDTO,
    RecommendationDTO,
    PredictionDTO,
    RatingCreateDTO
)

from ..constants import NOTIFICATIONS_QUEUE


class ClassifierService(ABC):
    @abstractmethod
    async def predict(self, applicant: ApplicantPredictDTO) -> Optional[PredictionDTO]: pass

    @abstractmethod
    async def predict_batch(
            self,
            applicants: list[ApplicantPredictDTO]
    ) -> Optional[list[PredictionDTO]]: pass


class RecommendationService(ABC):
    @abstractmethod
    async def recommend(
            self,
            applicant: ApplicantRecommendDTO,
            top_n: int
    ) -> Optional[list[RecommendationDTO]]: pass


class TelegramUserService(ABC):
    @abstractmethod
    async def get_notifications(self, user_id: UUID) -> Optional[list[Notification]]: pass


class ProfileRepository(ABC):
    @abstractmethod
    async def create(self, profile: Profile) -> ProfileReadDTO: pass

    @abstractmethod
    async def read(self, user_id: UUID) -> Optional[ProfileReadDTO]: pass

    @abstractmethod
    async def update(self, profile: Profile) -> Optional[ProfileReadDTO]: pass

    @abstractmethod
    async def delete(self, user_id: UUID) -> Optional[ProfileReadDTO]: pass

    @abstractmethod
    async def get_by_applicant_id(self, applicant_id: int) -> Optional[ProfileReadDTO]: pass

    @abstractmethod
    async def get_applicants(self, user_id: UUID) -> list[Optional[ApplicantReadDTO]]: pass

    @abstractmethod
    async def get_applicant_points(self, user_id: UUID) -> int: pass


class ApplicantRepository(ABC):
    @abstractmethod
    async def create(self, applicant: ApplicantCreateDTO) -> None: pass

    @abstractmethod
    async def bulk_create(self, applicants: list[ApplicantCreateDTO]) -> None: pass

    @abstractmethod
    async def read(self, applicant_id: int) -> list[ApplicantReadDTO]: pass

    @abstractmethod
    async def get_by_direction(self, direction: str) -> list[ApplicantReadDTO]: pass

    @abstractmethod
    async def paginate(self, page: int, limit: int) -> list[ApplicantReadDTO]: pass

    @abstractmethod
    async def paginate_by_direction(
            self,
            direction: str,
            page: int,
            limit: int
    ) -> list[ApplicantReadDTO]: pass

    @abstractmethod
    async def sort_by_probability(self, applicant_id: int) -> list[ApplicantReadDTO]: pass

    @abstractmethod
    async def sort_by_priority(self, applicant_id: int) -> list[ApplicantReadDTO]: pass

    @abstractmethod
    async def count(self) -> int: pass


class RatingRepository(ABC):
    @abstractmethod
    async def bulk_create(self, rating_position: list[RatingCreateDTO]) -> None: pass

    @abstractmethod
    async def read(self, applicant_id: int, direction: str) -> list[Rating]: pass


class BaseConditionalChecker(ABC):
    _applicant: "ApplicantReadDTO"
    _rating_history: "RatingHistory"

    @abstractmethod
    def check(self) -> bool: pass


class BaseBroker(Protocol):
    async def publish(
            self,
            messages: BaseModel | list[BaseModel] | dict,
            queue: str = NOTIFICATIONS_QUEUE
    ) -> None: pass
