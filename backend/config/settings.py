from pydantic_settings import BaseSettings
from pydantic import ConfigDict, Field, field_validator, model_validator
from typing import Optional


class Settings(BaseSettings):
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # App
    app_name: str = Field(default="Robolearn API", description="Application name")
    app_version: str = Field(default="1.0.0", description="Application version")
    debug: bool = Field(default=False, description="Enable debug mode")
    node_env: str = Field(default="production", description="Environment: development, production, or test")

    # Security
    secret_key: str = Field(default="", description="Secret key for JWT signing (REQUIRED when not using RS256)")
    algorithm: str = Field(default="HS256", description="JWT signing algorithm")
    access_token_expire_minutes: int = Field(default=60, description="JWT token expiration in minutes", ge=1, le=525600)
    jwt_private_key: str = Field(default="", description="RSA private key for RS256 JWT signing (optional)")
    jwt_public_key: str = Field(default="", description="RSA public key for RS256 JWT verification (optional)")

    # PostgreSQL
    postgres_user: str = Field(default="postgres", description="PostgreSQL username")
    postgres_password: str = Field(default="", description="PostgreSQL password")
    postgres_host: str = Field(default="localhost", description="PostgreSQL host")
    postgres_port: int = Field(default=5432, description="PostgreSQL port", ge=1, le=65535)
    postgres_db: str = Field(default="robolearn", description="PostgreSQL database name")

    # MongoDB
    mongodb_url: str = Field(default="mongodb://localhost:27017", description="MongoDB connection URL")
    mongodb_db: str = Field(default="robolearn_metrics", description="MongoDB database name")

    # Dialogflow
    dialogflow_project_id: Optional[str] = Field(default=None, description="Google Dialogflow project ID")
    google_credentials_path: Optional[str] = Field(default=None, description="Path to Google service account JSON")

    # Redis
    redis_url: str = Field(default="redis://localhost:6379/0", description="Redis connection URL")
    redis_password: str = Field(default="", description="Redis password (optional)")

    # Ollama / Local LLM
    ollama_url: str = Field(default="http://localhost:11434", description="Ollama API base URL")
    ollama_model: str = Field(default="qwen2.5:3b", description="Ollama model name")

    # CORS
    cors_origins: list = Field(
        default=["http://localhost:3000"],
        description="Comma-separated list of allowed CORS origins",
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
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

    @field_validator("node_env")
    @classmethod
    def validate_node_env(cls, v):
        allowed = {"development", "production", "test"}
        if v.lower() not in allowed:
            raise ValueError(f"NODE_ENV must be one of: {', '.join(sorted(allowed))}")
        return v.lower()

    @field_validator("ollama_url", "mongodb_url", "redis_url")
    @classmethod
    def validate_url(cls, v):
        if v and not v.startswith(("http://", "https://", "mongodb://", "redis://", "rediss://")):
            raise ValueError(f"Invalid URL scheme: {v}")
        return v

    @model_validator(mode="after")
    def validate_dialogflow_config(self):
        df_id = self.dialogflow_project_id
        creds = self.google_credentials_path
        if df_id and not creds:
            raise ValueError("google_credentials_path is required when dialogflow_project_id is set")
        if creds and not df_id:
            raise ValueError("dialogflow_project_id is required when google_credentials_path is set")
        return self

    @model_validator(mode="after")
    def inject_redis_password(self):
        if self.redis_password:
            parts = self.redis_url.split("://", 1)
            if len(parts) == 2 and ":" not in parts[1].split("@")[0]:
                self.redis_url = f"{parts[0]}://:{self.redis_password}@{parts[1]}"
        elif self.node_env == "production":
            raise ValueError("REDIS_PASSWORD is required when NODE_ENV=production")
        return self

    @model_validator(mode="after")
    def auto_algorithm_for_rsa(self):
        if self.jwt_private_key and self.jwt_public_key:
            self.algorithm = "RS256"
        return self


settings = Settings()
