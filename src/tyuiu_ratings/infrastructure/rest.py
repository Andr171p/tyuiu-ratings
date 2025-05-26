from typing import Optional

import logging
from uuid import UUID

import aiohttp

from ..core.domain import Notification
from ..core.dto import (
    ApplicantPredictDTO,
    ApplicantRecommendDTO,
    RecommendationDTO
)
from ..core.interfaces import (
    AdmissionClassifierService,
    RecommendationSystemService,
    TelegramUserService
)


class AdmissionClassifierAPI(AdmissionClassifierService):
    def __init__(self, base_url: str) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)
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
            self.logger.error("Error while predict: %s", e)

    async def predict_batch(self, applicants: list[ApplicantPredictDTO]) -> Optional[list[float]]:
        try:
            url = f"{self.base_url}/api/v1/classifier/predict"
            headers = {"Content-Type": "application/json; charset=UTF-8"}
            applicants = {"applicants": applicant.model_dump() for applicant in applicants}
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url=url,
                    headers=headers,
                    json=applicants
                ) as response:
                    data = await response.json()
            return [probability for probability in data["probabilities"]]
        except aiohttp.ClientError as e:
            self.logger.error("Error while predict batch: %s", e)


class RecommendationSystemAPI(RecommendationSystemService):
    def __init__(self, base_url: str) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)
        self.base_url = base_url

    async def recommend(self, applicant: ApplicantRecommendDTO) -> Optional[list[RecommendationDTO]]:
        url = f"{self.base_url}/api/v1/recommendations/"
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
                RecommendationDTO.model_validate(direction)
                for direction in data["directions"]
            ]
        except aiohttp.ClientError as e:
            self.logger.error("Error while recommend directions: %s", e)


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
            return [Notification.model_validate(notification) for notification in data["notification"]]
        except aiohttp.ClientError as e:
            self.logger.error("Error while receiving notifications: %s", e)
