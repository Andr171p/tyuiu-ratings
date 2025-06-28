from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..profiles.schemas import Profile

from abc import ABC, abstractmethod

from .dto import (
    ApplicantPredict,
    ApplicantRecommend,
    ApplicantCreate,
    Prediction,
    Recommendation,
    CreatedApplicant
)


class ClassifierService(ABC):
    @abstractmethod
    async def predict(self, applicant: ApplicantPredict) -> Prediction: pass

    @abstractmethod
    async def predict_batch(self, applicants: list[ApplicantPredict]) -> list[Prediction]: pass


class RecommendationService(ABC):
    @abstractmethod
    async def recommend(self, applicant: ApplicantRecommend, top_n: int) -> list[Recommendation]: pass


class ApplicantRepository(ABC):
    @abstractmethod
    async def bulk_upsert(self, applicants: list[ApplicantCreate]) -> None: pass

    @abstractmethod
    async def read(self, applicant_id: int) -> list[CreatedApplicant]: pass

    @abstractmethod
    async def get_profile(self, applicant_id: int) -> Optional["Profile"]: pass

    @abstractmethod
    async def get_applicant(self, applicant_id: int, direction: str) -> Optional[CreatedApplicant]: pass

    @abstractmethod
    async def get_applicants_by_direction(self, direction: str) -> list[CreatedApplicant]: pass

    @abstractmethod
    async def paginate(self, page: int, limit: int) -> list[CreatedApplicant]: pass

    @abstractmethod
    async def paginate_by_direction(
            self,
            direction: str,
            page: int,
            limit: int
    ) -> list[CreatedApplicant]: pass

    @abstractmethod
    async def sort_by_probability(self, applicant_id: int) -> list[CreatedApplicant]: pass

    @abstractmethod
    async def count(self) -> int: pass
