import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

from .constants import ENV_PATH, PG_DRIVER


load_dotenv(ENV_PATH)


class APISettings(BaseSettings):
    CLASSIFIER_URL: str = os.getenv("CLASSIFIER_URL")
    REC_SYS: str = os.getenv("REC_SYS_URL")


class RedisSettings(BaseSettings):
    REDIS_HOST: str = os.getenv("REDIS_HOST")
    REDIS_PORT: int = os.getenv("REDIS_PORT")

    @property
    def redis_url(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/0"


class PostgresSettings(BaseSettings):
    PG_HOST: str = os.getenv("POSTGRES_HOST")
    PG_PORT: int = os.getenv("POSTGRES_PORT")
    PG_USER: str = os.getenv("POSTGRES_USER")
    PG_PASSWORD: str = os.getenv("POSTGRES_PASSWORD")
    PG_DB: str = os.getenv("POSTGRES_DB")

    @property
    def sqlalchemy_url(self) -> str:
        return f"postgresql+{PG_DRIVER}://{self.PG_USER}:{self.PG_PASSWORD}@{self.PG_HOST}:{self.PG_PORT}/{self.PG_DB}"


class RabbitSettings(BaseSettings):
    RABBIT_HOST: str = os.getenv("RABBIT_HOST")
    RABBIT_PORT: int = os.getenv("RABBIT_PORT")
    RABBIT_USER: str = os.getenv("RABBIT_USER")
    RABBIT_PASSWORD: str = os.getenv("RABBIT_PASSWORD")

    @property
    def rabbit_url(self) -> str:
        return f"amqp://{self.RABBIT_USER}:{self.RABBIT_PASSWORD}@{self.RABBIT_HOST}:{self.RABBIT_PORT}/"


class Settings(BaseSettings):
    api: APISettings = APISettings()
    redis: RedisSettings = RedisSettings()
    postgres: PostgresSettings = PostgresSettings()
    rabbit: RabbitSettings = RabbitSettings()
