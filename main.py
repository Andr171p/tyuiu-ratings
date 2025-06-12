'''import logging

from src.tyuiu_ratings.api import create_fastapi_app


logging.basicConfig(level=logging.INFO)

app = create_fastapi_app()'''


from src.tyuiu_ratings.profile.dto import ProfileRefactoring


profile = ProfileRefactoring(
    applicant_id=1,
    gender="male"
)

print(profile.model_dump(exclude_none=True))
