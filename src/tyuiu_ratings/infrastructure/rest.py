from typing import Optional

import logging
from uuid import UUID

import aiohttp

from ..core.domain import Notification
from ..core.exception import PredictionError, RecommendationError, TelegramError
from ..core.dto import ApplicantPredictDTO, ApplicantRecommendDTO, RecommendationDTO, PredictionDTO
from ..core.base import ClassifierService, RecommendationService, TelegramUserService


class ClassifierAPI(ClassifierService):
    def __init__(self, base_url: str) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)
        self.base_url = base_url

    async def predict(self, applicant: ApplicantPredictDTO) -> Optional[PredictionDTO]:
        try:
            url = f"{self.base_url}/api/v1/classifier/predict"
            headers = {"Content-Type": "application/json; charset=UTF-8"}
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url=url,
                    headers=headers,
                    json=applicant.model_dump()
                ) as response:
                    prediction = await response.json()
            return PredictionDTO.model_validate(prediction)
        except aiohttp.ClientError as e:
            self.logger.error("Error while predict: %s", e)
            raise PredictionError(f"Error while predict: {e}") from e

    async def predict_batch(self, applicants: list[ApplicantPredictDTO]) -> list[PredictionDTO]:
        try:
            url = f"{self.base_url}/api/v1/classifier/predict"
            headers = {"Content-Type": "application/json; charset=UTF-8"}
            applicants = {"applicant": applicant.model_dump() for applicant in applicants}
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url=url,
                    headers=headers,
                    json=applicants
                ) as response:
                    predictions = await response.json()
            return [PredictionDTO.model_validate(prediction) for prediction in predictions]
        except aiohttp.ClientError as e:
            self.logger.error("Error while predict batch: %s", e)
            raise PredictionError(f"Error while predict batch: {e}") from e


class RecommendationAPI(RecommendationService):
    def __init__(self, base_url: str) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)
        self.base_url = base_url

    async def recommend(
            self,
            applicant: ApplicantRecommendDTO,
            top_n: int
    ) -> list[RecommendationDTO]:
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
                RecommendationDTO(direction_id=direction["direction_id"], direction=direction["name"])
                for direction in data["directions"]
            ]
        except aiohttp.ClientError as e:
            self.logger.error("Error while recommend directions: %s", e)
            raise RecommendationError(f"Error while recommend directions: {e}") from e


class TelegramUserAPI(TelegramUserService):
    def __init__(self, base_url: str) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)
        self.base_url = base_url

    async def get_notifications(self, user_id: UUID) -> Optional[list[Notification]]:
        url = f"{self.base_url}/api/v1/users/{user_id}/notifications"
        headers = {"Content-Type": "application/json; charset=UTF-8"}
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url=url, headers=headers) as response:
                    data = await response.json()
            return [Notification.model_validate(notification) for notification in data]
        except aiohttp.ClientError as e:
            self.logger.error("Error while receiving notifications: %s", e)
            raise TelegramError(f"Error while receiving notifications: {e}") from e
