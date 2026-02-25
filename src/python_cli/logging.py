"""Central logging configuration using Loguru."""

from __future__ import annotations

import sys
from pathlib import Path

from loguru import logger


def configure_logging(level: str = "INFO") -> None:
    """Configure console + rotating file logs."""
    logger.remove()

    logs_dir = Path.home() / ".python-cli" / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)

    console_format = (
        "<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )
    logger.add(
        sys.stderr,
        level=level,
        colorize=True,
        format=console_format,
    )

    logger.add(
        str(logs_dir / "python-cli_{time:YYYY-MM-DD_HH-mm-ss}.log"),
        level="DEBUG",
        rotation="10 MB",
        retention="7 days",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
    )
