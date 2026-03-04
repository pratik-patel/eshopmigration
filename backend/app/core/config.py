"""
Application configuration using pydantic-settings.
Environment variables override defaults.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    """Application settings with environment variable overrides."""

    # Application
    app_name: str = "eShop Catalog Management"
    debug: bool = False

    # Database
    db_url: str = "sqlite+aiosqlite:///./eshop.db"

    # CORS
    cors_origins: List[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    # Logging
    log_level: str = "INFO"

    # File storage
    pics_directory: str = "./Pics"
    temp_upload_directory: str = "./temp_uploads"
    max_image_size_mb: int = 10

    # JWT Authentication (for future implementation)
    secret_key: str = "development-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Pagination defaults
    default_page_size: int = 10
    max_page_size: int = 100

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


# Global settings instance
_settings: Settings | None = None


def get_settings() -> Settings:
    """Get cached settings instance."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
