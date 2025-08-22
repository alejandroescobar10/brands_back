from typing import List, Any
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
import json

class Settings(BaseSettings):
    database_url: str
    cors_allow_origins: List[str] = ["*"]
    debug: bool = False  # ← NUEVO (mapea DEBUG del .env)

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,   # DEBUG o debug funcionan
        extra="ignore",         # ignora claves desconocidas en .env
    )

    @field_validator("cors_allow_origins", mode="before")
    @classmethod
    def parse_cors(cls, v: Any) -> List[str]:
        if v is None or (isinstance(v, str) and v.strip() == ""):
            return ["*"]
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            s = v.strip()
            if s.startswith("["):  # JSON
                return json.loads(s)
            return [item.strip() for item in s.split(",") if item.strip()]
        return v

settings = Settings()
