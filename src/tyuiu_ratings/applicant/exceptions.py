

class PredictionError(Exception):
    pass


class RecommendationError(Exception):
    pass


class ApplicantsCreationError(Exception):
    pass


class ApplicantsReadingError(Exception):
    pass


class UseCaseError(Exception):
    pass


class DirectionsRecommendationError(UseCaseError):
    pass
