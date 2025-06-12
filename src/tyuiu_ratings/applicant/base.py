from abc import ABC, abstractmethod

from .dto import (
    ApplicantPredict,
    ApplicantRecommend,
    ApplicantCreate,
    Prediction,
    Recommendation
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
