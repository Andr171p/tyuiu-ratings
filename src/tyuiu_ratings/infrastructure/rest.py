import logging

from typing import List, Optional

import aiohttp

from ..core.dto import ApplicantPredictDTO, ApplicantRecommendDTO, RecommendedDirectionDTO
from ..core.interfaces import BinaryClassifier, RecommendationSystem


logger = logging.getLogger(__name__)


class BinaryClassifierApi(BinaryClassifier):
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url

    async def predict(self, applicant: ApplicantPredictDTO) -> Optional[float]:
        try:
            url = f"{self.base_url}/api/v1/classifier/predict"
            headers = {"Content-Type": "application/json; charset=UTF-8"}
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url=url,
                    headers=headers,
                    json=applicant.model_dump()
                ) as response:
                    data = await response.json()
            return data["probability"]
        except aiohttp.ClientError as e:
            logger.error("Error while predict: %s", e)

    async def predict_batch(self, applicants: List[ApplicantPredictDTO]) -> Optional[List[float]]:
        try:
            url = f"{self.base_url}/api/v1/classifier/predict"
            headers = {"Content-Type": "application/json; charset=UTF-8"}
            applicants = {"applicants": applicants}
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url=url,
                    headers=headers,
                    json=applicants
                ) as response:
                    data = await response.json()
            return [probability for probability in data["probabilities"]]
        except aiohttp.ClientError as e:
            logger.error("Error while predict batch: %s", e)


class RecommendationSystemApi(RecommendationSystem):
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url

    async def recommend(self, applicant: ApplicantRecommendDTO) -> Optional[List[RecommendedDirectionDTO]]:
        try:
            url = f"{self.base_url}/api/v1/recommendations/"
            headers = {"Content-Type": "application/json; charset=UTF-8"}
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url=url,
                    headers=headers,
                    json=applicant.model_dump()
                ) as response:
                    data = await response.json()
            return [
                RecommendedDirectionDTO.model_validate(direction)
                for direction in data["directions"]
            ]
        except aiohttp.ClientError as e:
            logger.error("Error while recommend directions: %s", e)
