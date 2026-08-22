from typing import List, Union
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
import os

class Settings(BaseSettings):
    # App Settings
    APP_NAME: str = "VOLT-LOGIC Battery Telemetry API"
    ENVIRONMENT: str = "production"
    DEBUG: bool = False
    PORT: int = 8000
    HOST: str = "0.0.0.0"

    # Database Settings (PostgreSQL / Supabase)
    # Default fallback to sqlite:///./volt_logic.db if DATABASE_URL is not set for local zero-infra demo
    DATABASE_URL: str = Field(
        default="sqlite:///./volt_logic.db",
        description="PostgreSQL or SQLite connection string"
    )

    # ML Model & API Key
    ML_MODEL_API_KEY: str = Field(
        default="",
        description="API Key for external ML Inference Service (e.g. HuggingFace / Hosted Model)"
    )
    EXTERNAL_ML_ENDPOINT: str = Field(
        default="",
        description="Optional external ML inference endpoint URL"
    )
    MODEL_VERSION: str = "v2.0.0-battery-eis"
    MODEL_PATH: str = os.path.join(os.path.dirname(__file__), "model", "classifier.joblib")

    # Security & CORS
    CORS_ORIGINS: Union[List[str], str] = Field(
        default=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000", "http://127.0.0.1:3000"]
    )
    
    # Rate Limiting
    RATE_LIMIT_PREDICT: str = "20/minute"
    RATE_LIMIT_HISTORY: str = "30/minute"
    RATE_LIMIT_DEFAULT: str = "60/minute"

    # Payload Size Limitation (in bytes, 10 KB = 10240)
    MAX_REQUEST_BODY_SIZE: int = 10 * 1024

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, list):
            return v
        return ["http://localhost:5173", "http://127.0.0.1:5173"]

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(__file__), ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
