from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    database_url: str
    cors_allow_origins: List[str] = ["*"]

    class Config:
        env_file = ".env"

settings = Settings()
