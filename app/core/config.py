"""
Centralized application settings.
Loads configuration from environment variables and .env file.
"""

import os
from pathlib import Path
from pydantic_settings import BaseSettings


# Project root directory (2 levels up from this file: app/core/config.py → project root)
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Groq LLM API
    groq_api_key: str = ""
    groq_model: str = "llama-3.3-70b-versatile"

    # Data & Model Paths (relative to project root)
    data_dir: str = str(PROJECT_ROOT / "data")
    model_dir: str = str(PROJECT_ROOT / "data" / "models")
    processed_data_dir: str = str(PROJECT_ROOT / "data" / "processed")

    raw_data_dir: str = str(PROJECT_ROOT / "data" / "raw")

    # API Server
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # Frontend
    api_base_url: str = "http://localhost:8000"

    class Config:
        env_file = str(PROJECT_ROOT / ".env")
        env_file_encoding = "utf-8"
        extra = "ignore"

    @property
    def profile_model_path(self) -> str:
        return os.path.join(self.model_dir, "profile_type_xgb_pipeline.joblib")

    @property
    def label_encoder_path(self) -> str:
        return os.path.join(self.model_dir, "label_encoder.joblib")

    @property
    def skill_recommender_path(self) -> str:
        return os.path.join(self.model_dir, "skill_recommender.joblib")

    @property
    def combined_csv_path(self) -> str:
        return os.path.join(self.processed_data_dir, "combined.csv")




settings = Settings()
