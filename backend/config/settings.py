from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # App
    app_name: str = "Robolearn API"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # Security
    secret_key: str = "your-secret-key-change-in-production-robolearn"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 10080  # 7 days
    
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
    cors_origins: list = ["http://localhost:3000", "http://localhost:5173", "http://localhost:8000"]
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
