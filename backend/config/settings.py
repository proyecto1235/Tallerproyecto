from pydantic_settings import BaseSettings
from pydantic import ConfigDict, field_validator
from typing import Optional

class Settings(BaseSettings):
    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore"
    )

    # App
    app_name: str = "Robolearn API"
    app_version: str = "1.0.0"
    debug: bool = False
    node_env: str = "production"

    # Security
    secret_key: str = ""
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    # PostgreSQL
    postgres_user: str = "postgres"
    postgres_password: str = ""
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "robolearn"

    # MongoDB
    mongodb_url: str = "mongodb://localhost:27017"
    mongodb_db: str = "robolearn_metrics"

    # Dialogflow
    dialogflow_project_id: Optional[str] = None
    google_credentials_path: Optional[str] = None

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Ollama / Local LLM
    ollama_url: str = "http://localhost:11434"
    ollama_model: str = "qwen2.5:3b"

    # CORS
    cors_origins: list = [
        "http://localhost:3000"
    ]

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS origins from string or list format"""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    @field_validator("secret_key")
    @classmethod
    def validate_secret_key(cls, v):
        if not v or v == "" or "change-in-production" in v.lower() or "your-secret" in v.lower():
            raise ValueError(
                "SECRET_KEY must be set to a strong, unique value in production. "
                "Generate one with: python -c \"import secrets; print(secrets.token_urlsafe(32))\""
            )
        return v

settings = Settings()
