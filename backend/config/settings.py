from pydantic_settings import BaseSettings
from pydantic import ConfigDict, field_validator
from typing import Optional
from pathlib import Path

class Settings(BaseSettings):
    model_config = ConfigDict(
        env_file=str(Path(__file__).parent.parent / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    app_name: str = "Robolearn API"
    app_version: str = "1.0.0"
    debug: bool = False
    app_env: Optional[str] = "development"

    secret_key: str = ""
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 10080

    postgres_user: str = "postgres"
    postgres_password: str = "123123123"
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "robolearn"
    db_pool_min: int = 5
    db_pool_max: int = 50

    mongodb_url: str = "mongodb://localhost:27017"
    mongodb_db: str = "robolearn_metrics"

    dialogflow_project_id: Optional[str] = None
    dialogflow_agent_id: Optional[str] = None
    google_credentials_path: Optional[str] = None

    redis_url: str = "redis://localhost:6379/0"

    ollama_url: str = "http://localhost:11434"
    ollama_model: str = "qwen2.5-coder:1.5b"

    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-3.5-turbo"

    ml_model_dir: str = "models"

    cors_origins: list = ["*"]

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

settings = Settings()
