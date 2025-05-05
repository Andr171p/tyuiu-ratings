import asyncio

from src.tyuiu_ratings.settings import Settings
from src.tyuiu_ratings.core.dto import ApplicantPredictDTO
from src.tyuiu_ratings.infrastructure.rest import BinaryClassifierApi


async def main() -> None:
    api = BinaryClassifierApi(Settings().micro_services.BINARY_CLASSIFIER_URL)
    applicant = ApplicantPredictDTO(
        gender="female",
        gpa=5,
        points=219,
        direction="09.03.00 Информатика и вычислительная техника"
    )
    proba = await api.predict(applicant)
    print(proba)


asyncio.run(main())
