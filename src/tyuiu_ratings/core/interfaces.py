from typing import Optional, List, Protocol, Union

from abc import ABC, abstractmethod

from uuid import UUID

from pydantic import BaseModel

from .domain import Profile, RatingPosition, Notification
from .dto import (
    ProfileReadDTO,
    ApplicantReadDTO,
    ApplicantCreateDTO,
    ApplicantPredictDTO,
    ApplicantRecommendDTO,
    RecommendedDirectionDTO
)
from ..constants import NOTIFICATIONS_QUEUE


class AdmissionClassifier(ABC):
    @abstractmethod
    async def predict(self, applicant: ApplicantPredictDTO) -> Optional[float]: pass

    @abstractmethod
    async def predict_batch(self, applicants: list[ApplicantPredictDTO]) -> Optional[list[float]]: pass


class RecommendationSystem(ABC):
    @abstractmethod
    async def recommend(self, applicant: ApplicantRecommendDTO) -> Optional[list[RecommendedDirectionDTO]]: pass


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


class ApplicantRepository(ABC):
    @abstractmethod
    async def create(self, applicant: ApplicantCreateDTO) -> None: pass

    @abstractmethod
    async def bulk_create(self, applicants: list[ApplicantCreateDTO]) -> None: pass

    @abstractmethod
    async def read(self, applicant_id: int) -> Optional[ApplicantReadDTO]: pass

    @abstractmethod
    async def get_by_direction(self, direction: str) -> list[ApplicantReadDTO]: pass

    @abstractmethod
    async def get_by_applicant_id(self, applicant_id: int) -> list[ApplicantReadDTO]: pass

    @abstractmethod
    async def paginate(self, page: int, limit: int) -> list[ApplicantReadDTO]: pass

    @abstractmethod
    async def paginate_by_direction(
            self,
            direction: str,
            page: int,
            limit: int
    ) -> List[ApplicantReadDTO]: pass

    @abstractmethod
    async def sort_by_probability(self, applicant_id: int) -> list[ApplicantReadDTO]: pass

    @abstractmethod
    async def count(self) -> int: pass


class HistoryRepository(ABC):
    @abstractmethod
    async def bulk_create(self, rating_position: list[RatingPosition]) -> None: pass

    @abstractmethod
    async def read(self, applicant_id: int) -> list[RatingPosition]: pass


class BaseNotificationSender(ABC):
    @abstractmethod
    async def send(self, user_id: UUID, applicant: ApplicantReadDTO) -> None: pass


class AMQPBroker(Protocol):
    async def publish(
            self,
            messages: Union[BaseModel, list[BaseModel]],
            queue: str = NOTIFICATIONS_QUEUE
    ) -> None: pass
