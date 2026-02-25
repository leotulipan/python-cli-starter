"""Typer CLI application."""

from __future__ import annotations

import typer
from loguru import logger
from rich.console import Console

from python_cli.commands.hello import hello
from python_cli.config import get_settings
from python_cli.errors import AppError
from python_cli.logging import configure_logging
from python_cli.version import __version__

app = typer.Typer(no_args_is_help=True, help="Generic Python CLI scaffold")
console = Console()


@app.callback()
def main(
    version: bool = typer.Option(False, "--version", help="Show version and exit"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose logging"),
) -> None:
    if version:
        console.print(f"python-cli {__version__}")
        raise typer.Exit()

    settings = get_settings()
    log_level = "DEBUG" if verbose else settings.log_level
    configure_logging(log_level)
    logger.debug("CLI initialized")


@app.command()
def greet(name: str = typer.Argument(..., help="Name to greet")) -> None:
    """Say hello."""
    hello(name)


@app.command()
def fail() -> None:
    """Example of a controlled error."""
    raise AppError("Something went wrong", exit_code=2)


@app.exception_handler(AppError)
def handle_app_error(request: typer.Request, exc: AppError) -> None:  # type: ignore[valid-type]
    logger.error(exc.message)
    raise typer.Exit(exc.exit_code)
