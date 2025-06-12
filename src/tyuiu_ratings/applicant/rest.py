import logging

import aiohttp

from .base import ClassifierService, RecommendationService
from .dto import ApplicantPredict, ApplicantRecommend, Prediction, Recommendation
from .exceptions import PredictionError, RecommendationError


class ClassifierAPI(ClassifierService):
    def __init__(self, base_url: str) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)
        self.base_url = base_url

    async def predict(self, applicant: ApplicantPredict) -> Prediction:
        url = f"{self.base_url}/api/v1/classifier/predict"
        headers = {"Content-Type": "application/json; charset=UTF-8"}
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url=url,
                    headers=headers,
                    json=applicant.model_dump()
                ) as response:
                    prediction = await response.json()
            return Prediction.model_validate(prediction)
        except aiohttp.ClientError as e:
            self.logger.error(f"Error while predict: {e}")
            raise PredictionError(f"Error while predict: {e}") from e

    async def predict_batch(self, applicants: list[ApplicantPredict]) -> list[Prediction]:
        url = f"{self.base_url}/api/v1/classifier/predict-batch"
        headers = {"Content-Type": "application/json; charset=UTF-8"}
        applicants = {"applicants": [applicant.model_dump() for applicant in applicants]}
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url=url,
                    headers=headers,
                    json=applicants
                ) as response:
                    predictions = await response.json()
            return [Prediction.model_validate(prediction) for prediction in predictions]
        except aiohttp.ClientError as e:
            self.logger.error(f"Error while predict batch: {e}")
            raise PredictionError(f"Error while predict batch: {e}") from e


class RecommendationAPI(RecommendationService):
    def __init__(self, base_url: str) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)
        self.base_url = base_url

    async def recommend(self, applicant: ApplicantRecommend, top_n: int) -> list[Recommendation]:
        url = f"{self.base_url}/api/v1/recommendations/?top_n={top_n}"
        headers = {"Content-Type": "application/json; charset=UTF-8"}
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url=url,
                    headers=headers,
                    json=applicant.model_dump()
                ) as response:
                    data = await response.json()
            return [
                Recommendation(direction_id=direction["direction_id"], direction=direction["name"])
                for direction in data["directions"]
            ]
        except aiohttp.ClientError as e:
            self.logger.error(f"Error while recommend directions: {e}")
            raise RecommendationError(f"Error while recommend directions: {e}") from e
