"""
Application configuration loaded from environment variables.

Uses pydantic-settings for type-safe, validated configuration
with automatic .env file support.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Central configuration for the ShortLink API."""

    # Database
    database_url: str = "sqlite:///./shortlink.db"

    # Service
    base_url: str = "http://localhost:8000"
    short_code_length: int = 6

    # CORS: comma-separated origins or "*" for all
    cors_origins: str = "*"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
