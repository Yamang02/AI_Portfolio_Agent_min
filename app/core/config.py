import os
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

_env = os.getenv("APP_ENV", "local")


class Settings(BaseSettings):
    app_env: str = "local"
    ollama_url: str = "http://localhost:11434"
    model_name: str = "llama3:8b"
    allowed_origins: list[str] = ["*"]
    rate_limit_rpm: int = 60
    log_level: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=f".env.{_env}",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
