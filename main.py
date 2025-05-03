import asyncio

from src.tyuiu_ratings.settings import Settings
from src.tyuiu_ratings.core.dto import ApplicantPredictDTO
from src.tyuiu_ratings.infrastructure.rest import BinaryClassifierApi


async def main() -> None:
    api = BinaryClassifierApi(Settings().micro_services.binary_classifier_url)
    applicant = ApplicantPredictDTO(
        gender="male",
        gpa=4,
        points=227,
        direction="09.03.00 Информатика и вычислительная техника"
    )
    proba = await api.predict(applicant)
    print(proba)


asyncio.run(main())
