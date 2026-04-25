"""
Centralized application configuration using Pydantic BaseSettings.
Values are loaded from environment variables or an .env file.
"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Application metadata
    APP_NAME: str = "Retail Analytics & Forecasting API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = "sqlite:///./retail_analytics.db"

    # API configuration
    API_V1_PREFIX: str = "/api/v1"
    ALLOWED_ORIGINS: list[str] = ["*"]

    # ML configuration
    FORECAST_HORIZON_DAYS: int = 30
    LGBM_NUM_BOOST_ROUNDS: int = 500
    KMEANS_N_CLUSTERS: int = 4

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Singleton settings instance
settings = Settings()
