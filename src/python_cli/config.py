"""Configuration management using pydantic-settings."""

from __future__ import annotations

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

_ENV_TEMPLATE = """\
# Runtime environment: dev | staging | prod
APP_ENV=dev

# Log verbosity: DEBUG | INFO | WARNING | ERROR
LOG_LEVEL=INFO

# Optional: directory for persistent data files (leave blank for default)
DATA_DIR=
"""


def ensure_config_dir() -> Path:
    """Create ~/.python-cli/ and write a blank .env template if none exists."""
    config_dir = Path.home() / ".python-cli"
    config_dir.mkdir(exist_ok=True)
    env_file = config_dir / ".env"
    if not env_file.exists():
        env_file.write_text(_ENV_TEMPLATE, encoding="utf-8")
    return config_dir


def _collect_env_files() -> tuple[str, ...]:
    """Return all existing .env paths ordered lowest-to-highest priority.

    pydantic-settings loads them in sequence; later files win on conflicts.
    """
    candidates: list[Path] = []

    home_env = Path.home() / ".env"
    app_env = Path.home() / ".python-cli" / ".env"
    cwd_env = Path.cwd() / ".env"

    if home_env.exists():
        candidates.append(home_env.resolve())

    if app_env.exists():
        candidates.append(app_env.resolve())

    cwd_resolved = cwd_env.resolve()
    if cwd_env.exists() and cwd_resolved not in candidates:
        candidates.append(cwd_resolved)

    return tuple(str(p) for p in candidates)


_config_dir = ensure_config_dir()
_env_files = _collect_env_files()


class Settings(BaseSettings):
    """Application settings loaded from environment and .env files."""

    app_env: str = Field(default="dev", validation_alias="APP_ENV")
    log_level: str = Field(default="INFO", validation_alias="LOG_LEVEL")
    data_dir: Path | None = Field(default=None, validation_alias="DATA_DIR")

    model_config = SettingsConfigDict(
        env_file=_env_files if _env_files else None,
        env_file_encoding="utf-8",
        extra="ignore",
    )


_settings: Settings | None = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
