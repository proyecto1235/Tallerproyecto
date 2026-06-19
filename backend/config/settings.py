from pydantic_settings import BaseSettings
from pydantic import ConfigDict, field_validator, model_validator
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
    jwt_public_key: Optional[str] = None
    jwt_private_key: Optional[str] = None
    node_env: Optional[str] = "development"

    # REQUIRED via .env — no defaults for security
    postgres_user: str = ""
    postgres_password: str = ""
    postgres_host: str = ""
    postgres_port: int = 0
    postgres_db: str = ""
    db_pool_min: int = 5
    db_pool_max: int = 50

    # MongoDB — REQUIRED via .env
    mongodb_url: str = ""
    mongodb_db: str = ""

    # Dialogflow — optional, set via .env if using Dialogflow
    dialogflow_project_id: Optional[str] = ""
    google_credentials_path: Optional[str] = ""

    # Redis — REQUIRED via .env
    redis_url: str = ""

    # Ollama / Local LLM — set via .env
    ollama_url: str = ""
    ollama_model: str = ""

    # OpenAI — optional, set via .env if using OpenAI as additional fallback
    openai_api_key: Optional[str] = ""
    openai_model: str = ""

    ml_model_dir: str = "models"

    cors_origins: list = []

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    @model_validator(mode="after")
    def validate_required(self):
        required = {
            "postgres_user": "POSTGRES_USER",
            "postgres_password": "POSTGRES_PASSWORD",
            "postgres_host": "POSTGRES_HOST",
            "postgres_port": "POSTGRES_PORT",
            "postgres_db": "POSTGRES_DB",
            "mongodb_url": "MONGODB_URL",
            "mongodb_db": "MONGODB_DB",
            "redis_url": "REDIS_URL",
        }
        missing = []
        for attr, env_var in required.items():
            val = getattr(self, attr, None)
            if not val or (isinstance(val, int) and val == 0):
                missing.append(env_var)
        if missing:
            raise ValueError(
                f"Variables .env obligatorias faltantes: {', '.join(missing)}. "
                f"Revisa backend/.env o config/settings.py"
            )
        return self

settings = Settings()
