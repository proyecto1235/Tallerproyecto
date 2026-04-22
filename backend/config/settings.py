from pydantic_settings import BaseSettings
from pydantic import ConfigDict, field_validator
from typing import Optional

class Settings(BaseSettings):
    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore"  # Ignora campos no definidos del .env
    )

    # App
    app_name: str = "Robolearn API"
    app_version: str = "1.0.0"
    debug: bool = False
    node_env: Optional[str] = "development"  # Agregado para .env

    # Security
    secret_key: str = "your-secret-key-change-in-production-robolearn"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 10080

    # PostgreSQL
    postgres_user: str = "postgres"
    postgres_password: str = "postgres"
    postgres_host: str = "postgres"
    postgres_port: int = 5432
    postgres_db: str = "robolearn"

    # MongoDB
    mongodb_url: str = "mongodb://mongo:27017"
    mongodb_db: str = "robolearn_metrics"

    # Dialogflow
    dialogflow_project_id: Optional[str] = None
    dialogflow_agent_id: Optional[str] = None
    google_credentials_path: Optional[str] = None

    # CORS
    cors_origins: list = [
        "*"
    ]

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS origins from string or list format"""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

settings = Settings()