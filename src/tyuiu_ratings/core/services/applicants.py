from typing import List

from ..entities import Applicant
from ..dto import ApplicantPredictDTO, ApplicantCreateDTO, RecommendedDirectionDTO
from ..interfaces import BinaryClassifier, ApplicantRepository


class ApplicantsService:
    def __init__(self) -> None:
        ...

    async def process(self, applicants: List[Applicant]) -> None:
        ...

    async def get_recommendations(self) -> List[RecommendedDirectionDTO]:
        ...

    async def rerank_priorities(self, applicant_id: int) -> ...:
        ...
