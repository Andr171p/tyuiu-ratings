from typing import List, Optional
from abc import ABC, abstractmethod

from ..dto import (
    ApplicantPredictDTO,
    ApplicantRecommendDTO,
    RecommendedDirectionDTO
)


class BinaryClassifier(ABC):
    @abstractmethod
    async def predict(self, applicant: ApplicantPredictDTO) -> Optional[float]: pass

    @abstractmethod
    async def predict_batch(self, applicants: List[ApplicantPredictDTO]) -> Optional[List[float]]: pass


class RecommendationSystem(ABC):
    @abstractmethod
    async def recommend(self, applicant: ApplicantRecommendDTO) -> Optional[List[RecommendedDirectionDTO]]: pass

