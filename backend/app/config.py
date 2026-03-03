"""
Application configuration using pydantic-settings.
"""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    # Environment
    environment: str = "development"

    # Database
    database_url: str = "sqlite+aiosqlite:///./eshop_catalog.db"

    # CORS
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    # Mock data mode
    use_mock_adapters: bool = True  # Default to mock for development

    # Logging
    log_level: str = "INFO"

    # Pagination
    default_page_size: int = 10
    max_page_size: int = 100

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
