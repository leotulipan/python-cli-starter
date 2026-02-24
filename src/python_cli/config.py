"""Configuration management using pydantic-settings."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


def _find_env_file() -> Optional[Path]:
    cwd_env = Path.cwd() / ".env"
    if cwd_env.exists():
        return cwd_env

    home_env = Path.home() / ".env"
    if home_env.exists():
        return home_env

    return None


class Settings(BaseSettings):
    """Application settings loaded from environment and optional .env file."""

    app_env: str = Field(default="dev", validation_alias="APP_ENV")
    log_level: str = Field(default="INFO", validation_alias="LOG_LEVEL")
    data_dir: Optional[Path] = Field(default=None, validation_alias="DATA_DIR")

    model_config = SettingsConfigDict(
        env_file=str(_find_env_file()) if _find_env_file() else None,
        env_file_encoding="utf-8",
        extra="ignore",
    )


def get_settings() -> Settings:
    return Settings()
