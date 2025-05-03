import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic_settings import BaseSettings


BASE_DIR = Path(__file__).resolve().parent.parent.parent

ENV_PATH = BASE_DIR / ".env"

load_dotenv(ENV_PATH)


class MicroServicesSettings(BaseSettings):
    binary_classifier_url: str = "http://localhost:8000"


class Settings(BaseSettings):
    micro_services: MicroServicesSettings = MicroServicesSettings()
