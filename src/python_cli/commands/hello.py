"""Example command implementations."""

from __future__ import annotations

import typer
from rich.console import Console

console = Console()


def hello(name: str = typer.Argument(..., help="Name to greet")) -> None:
    console.print(f"Hello, [cyan]{name}[/cyan]!")
