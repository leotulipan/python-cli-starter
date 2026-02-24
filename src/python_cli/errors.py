"""Error types and exit codes."""

from dataclasses import dataclass


@dataclass
class AppError(Exception):
    message: str
    exit_code: int = 1
