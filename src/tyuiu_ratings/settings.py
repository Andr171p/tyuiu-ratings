import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

from .constants import BASE_DIR, ENV_PATH


load_dotenv(ENV_PATH)


class MicroServicesSettings(BaseSettings):
    BINARY_CLASSIFIER_URL: str = os.getenv("TYUIU_BINARY_CLASSIFIER_URL")


class Settings(BaseSettings):
    micro_services: MicroServicesSettings = MicroServicesSettings()
