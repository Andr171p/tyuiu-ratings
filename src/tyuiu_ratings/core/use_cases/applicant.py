

class ApplicantUseCase:
    async def process(self, applicants: List[Applicant]) -> None:
        ...

    async def get_recommendations(self, applicant_id: int) -> List[RecommendedDirectionDTO]:
        ...

    async def rerank_priorities(self, applicant_id: int) -> ...:
        ...