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
    async def predict_batch(self, applicant: list[ApplicantPredict]) -> list[Prediction]: pass


class RecommendationService(ABC):
    @abstractmethod
    async def recommend(self, applicant: ApplicantRecommend, top_n: int) -> list[Recommendation]: pass


class ApplicantRepository(ABC):
    @abstractmethod
    async def bulk_create(self, applicants: list[ApplicantCreate]) -> None: pass

    @abstractmethod
    async def read(self, applicant_id: int) -> list[CreatedApplicant]: pass

    @abstractmethod
    async def sort_by_probability(self, applicant_id: int) -> list[CreatedApplicant]: pass
