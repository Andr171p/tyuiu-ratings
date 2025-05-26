import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

from .constants import ENV_PATH


load_dotenv(ENV_PATH)


class APISettings(BaseSettings):
    CLASSIFIER_URL: str = os.getenv("CLASSIFIER_URL")
    REC_SYS: str = os.getenv("REC_SYS_URL")


class Settings(BaseSettings):
    api: APISettings = APISettings()
