from .core.entities import Applicant
from .core.interfaces import Classifier
from .core.dto import ApplicantCreateDTO, ApplicantPredictDTO


class ApplicantHandler:
    def __init__(self, classifier: Classifier) -> None:
        self.classifier = classifier

    async def handle(self, applicants: list[Applicant]) -> list[ApplicantCreateDTO]:
        applicant_predict_dtos = [
            ApplicantPredictDTO(points=applicant.points, direction=applicant.direction)
            for applicant in applicants
        ]
        probabilities = await self.classifier.predict_batch(applicant_predict_dtos)
        applicant_create_dtos = [
            ApplicantCreateDTO(

            )
            for probability in probabilities
        ]
