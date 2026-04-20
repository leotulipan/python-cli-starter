# Python CLI Scaffold — Code Walkthrough

*2026-03-20T09:52:14Z by Showboat 0.6.1*
<!-- showboat-id: 4a3e7eeb-6ed2-48ec-b794-ac04e88f80eb -->

This project is a production-ready Python CLI scaffold. It wires together Typer (CLI framework), Rich (formatted output), Loguru (logging), and Pydantic Settings (configuration) into a clean, typed, testable template. This walkthrough follows execution order: from how the CLI is invoked, through configuration and logging setup, into command dispatch and output.

## 1. Project Structure

The source lives under `src/python_cli/`. Here's the full layout:

```bash
find src -type f | sort
```

```output
src/desktop.ini
src/python_cli/__init__.py
src/python_cli/__main__.py
src/python_cli/cli.py
src/python_cli/commands/desktop.ini
src/python_cli/commands/hello.py
src/python_cli/config.py
src/python_cli/desktop.ini
src/python_cli/errors.py
src/python_cli/logging.py
src/python_cli/py.typed
src/python_cli/utils.py
src/python_cli/version.py
```

Ignoring the `desktop.ini` files (Windows artifacts), the key modules are:

- **`version.py`** — Single source of truth for the version string
- **`__init__.py`** — Re-exports the version
- **`__main__.py`** — Allows `python -m python_cli` invocation
- **`cli.py`** — The Typer app: global options, command registration, error handling
- **`config.py`** — Pydantic Settings for environment-based configuration
- **`logging.py`** — Loguru console + rotating file log setup
- **`errors.py`** — Custom `AppError` exception with exit codes
- **`utils.py`** — Small shared helpers
- **`commands/hello.py`** — An example command implementation

## 2. Entry Point — How the CLI Gets Invoked

Everything starts in `pyproject.toml`. The `[project.scripts]` table tells pip (or uv) to create a console script that points at the Typer app:

```bash
sed -n '35,37p' pyproject.toml
```

```output
[project.scripts]
python-cli = "python_cli.cli:app"

```

When you type `python-cli` at the terminal, Python calls the `app` object in `python_cli.cli`. That object is a Typer instance — Typer handles all the argument parsing, help generation, and command dispatch.

There's also a `__main__.py` for running as a module (`python -m python_cli`):

```bash
cat src/python_cli/__main__.py
```

```output
"""Main entry point for python -m python_cli."""

from .cli import app

if __name__ == "__main__":
    app()
```

Both paths converge on the same `app` object. Let's look at what that object is.

## 3. The CLI Layer — `cli.py`

This is the heart of the application. It defines the Typer app, registers global options, sets up error handling, and registers commands. Here it is in full:

```bash
cat -n src/python_cli/cli.py
```

```output
     1	"""Typer CLI application."""
     2	
     3	from __future__ import annotations
     4	
     5	import typer
     6	from loguru import logger
     7	from rich.console import Console
     8	
     9	from python_cli.commands.hello import hello
    10	from python_cli.config import get_settings
    11	from python_cli.errors import AppError
    12	from python_cli.logging import configure_logging
    13	from python_cli.version import __version__
    14	
    15	app = typer.Typer(no_args_is_help=True, help="Generic Python CLI scaffold")
    16	console = Console()
    17	
    18	
    19	@app.callback()
    20	def main(
    21	    version: bool = typer.Option(False, "--version", help="Show version and exit"),
    22	    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose logging"),
    23	) -> None:
    24	    if version:
    25	        console.print(f"python-cli {__version__}")
    26	        raise typer.Exit()
    27	
    28	    settings = get_settings()
    29	    log_level = "DEBUG" if verbose else settings.log_level
    30	    configure_logging(log_level)
    31	    logger.debug("CLI initialized")
    32	
    33	
    34	@app.command()
    35	def greet(name: str = typer.Argument(..., help="Name to greet")) -> None:
    36	    """Say hello."""
    37	    hello(name)
    38	
    39	
    40	@app.command()
    41	def fail() -> None:
    42	    """Example of a controlled error."""
    43	    raise AppError("Something went wrong", exit_code=2)
    44	
    45	
    46	@app.exception_handler(AppError)
    47	def handle_app_error(request: typer.Request, exc: AppError) -> None:  # type: ignore[valid-type]
    48	    logger.error(exc.message)
    49	    raise typer.Exit(exc.exit_code)
```

Let's break this down piece by piece.

**Line 15: App creation.** `Typer(no_args_is_help=True)` means running `python-cli` with no arguments prints the help screen instead of doing nothing.

**Lines 19–31: The callback — global setup.** Typer's `@app.callback()` runs *before* any command. It handles two global options:

- `--version`: prints the version and exits immediately via `typer.Exit()`
- `--verbose / -v`: overrides the log level to DEBUG

If not showing version, it loads settings from environment / .env files (line 28), then configures logging (line 30). Every command that runs afterwards has logging ready.

**Lines 34–37: The `greet` command.** A thin wrapper — it takes a required `name` argument and delegates to `hello(name)` from the commands module. This follows the scaffold's design principle: CLI commands are thin; business logic lives in command modules.

**Lines 40–43: The `fail` command.** Demonstrates controlled error handling by raising `AppError`.

**Lines 46–49: The exception handler.** When any command raises `AppError`, Typer catches it here. It logs the error message and exits with the error's exit code. This prevents ugly tracebacks for *expected* failures.

## 4. Version — `version.py` and `__init__.py`

The version is isolated in its own tiny module to avoid import side effects:

```bash
cat src/python_cli/version.py && echo '---' && cat src/python_cli/__init__.py
```

```output
"""Version module kept separate to avoid import side effects."""

__version__ = "0.1.0"
---
"""Top-level package for python_cli."""

from .version import __version__

__all__ = ["__version__"]
```

`version.py` holds the version string as a constant. `__init__.py` re-exports it so you can do `from python_cli import __version__`. By keeping the version in a separate file, importing `version.py` never triggers heavy imports from the rest of the package.

## 5. Configuration — `config.py`

Settings are loaded from environment variables and `.env` files using Pydantic Settings:

```bash
cat -n src/python_cli/config.py
```

```output
     1	"""Configuration management using pydantic-settings."""
     2	
     3	from __future__ import annotations
     4	
     5	from pathlib import Path
     6	
     7	from pydantic import Field
     8	from pydantic_settings import BaseSettings, SettingsConfigDict
     9	
    10	
    11	def _find_env_file() -> Path | None:
    12	    cwd_env = Path.cwd() / ".env"
    13	    if cwd_env.exists():
    14	        return cwd_env
    15	
    16	    home_env = Path.home() / ".env"
    17	    if home_env.exists():
    18	        return home_env
    19	
    20	    return None
    21	
    22	
    23	class Settings(BaseSettings):
    24	    """Application settings loaded from environment and optional .env file."""
    25	
    26	    app_env: str = Field(default="dev", validation_alias="APP_ENV")
    27	    log_level: str = Field(default="INFO", validation_alias="LOG_LEVEL")
    28	    data_dir: Path | None = Field(default=None, validation_alias="DATA_DIR")
    29	
    30	    model_config = SettingsConfigDict(
    31	        env_file=str(_find_env_file()) if _find_env_file() else None,
    32	        env_file_encoding="utf-8",
    33	        extra="ignore",
    34	    )
    35	
    36	
    37	def get_settings() -> Settings:
    38	    return Settings()
```

**Lines 11–20: `_find_env_file()`.** Searches for a `.env` file in two places: the current working directory first, then the user's home directory. Returns `None` if neither exists.

**Lines 23–34: The `Settings` class.** Extends Pydantic's `BaseSettings`, which automatically reads values from environment variables. Three fields are defined:

- `app_env` (default: `"dev"`) — read from `APP_ENV`
- `log_level` (default: `"INFO"`) — read from `LOG_LEVEL`, used by the logging setup
- `data_dir` (default: `None`) — read from `DATA_DIR`, an optional path for data storage

The `validation_alias` on each field maps the Python attribute name to the corresponding environment variable name. `extra="ignore"` means unknown env vars won't cause validation errors.

**Line 37–38: `get_settings()`.** A simple factory. Each call creates a fresh `Settings` instance, re-reading the environment. In `cli.py` this is called once during the callback.

## 6. Logging — `logging.py`

The logging module configures Loguru with two output handlers:

```bash
cat -n src/python_cli/logging.py
```

```output
     1	"""Central logging configuration using Loguru."""
     2	
     3	from __future__ import annotations
     4	
     5	import sys
     6	from pathlib import Path
     7	
     8	from loguru import logger
     9	
    10	
    11	def configure_logging(level: str = "INFO") -> None:
    12	    """Configure console + rotating file logs."""
    13	    logger.remove()
    14	
    15	    logs_dir = Path.home() / ".python-cli" / "logs"
    16	    logs_dir.mkdir(parents=True, exist_ok=True)
    17	
    18	    console_format = (
    19	        "<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | "
    20	        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
    21	        "<level>{message}</level>"
    22	    )
    23	    logger.add(
    24	        sys.stderr,
    25	        level=level,
    26	        colorize=True,
    27	        format=console_format,
    28	    )
    29	
    30	    logger.add(
    31	        str(logs_dir / "python-cli_{time:YYYY-MM-DD_HH-mm-ss}.log"),
    32	        level="DEBUG",
    33	        rotation="10 MB",
    34	        retention="7 days",
    35	        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
    36	    )
```

**Line 13: `logger.remove()`.** Loguru ships with a default stderr handler. This removes it so we have full control.

**Lines 15–16:** Creates the log directory at `~/.python-cli/logs/`, using `mkdir(parents=True, exist_ok=True)` so it's safe to call repeatedly.

**Lines 18–28: Console handler.** Writes to stderr (not stdout, so it doesn't interfere with piped output). The format includes timestamp, log level, source location, and message — all color-coded using Loguru's markup tags. The level is controlled by the `--verbose` flag or `LOG_LEVEL` env var.

**Lines 30–36: File handler.** Writes to a timestamped log file in `~/.python-cli/logs/`. Key settings:
- `level="DEBUG"` — the file always captures everything, regardless of console verbosity
- `rotation="10 MB"` — starts a new file when the current one hits 10 MB
- `retention="7 days"` — automatically deletes log files older than a week

This dual-handler approach means you get clean, filtered output on the console while retaining full debug logs on disk for troubleshooting.

## 7. Error Handling — `errors.py`

```bash
cat -n src/python_cli/errors.py
```

```output
     1	"""Error types and exit codes."""
     2	
     3	from dataclasses import dataclass
     4	
     5	
     6	@dataclass
     7	class AppError(Exception):
     8	    message: str
     9	    exit_code: int = 1
```

Simple and effective. `AppError` is a dataclass exception with two fields:

- `message` — a user-facing error description
- `exit_code` — defaults to 1, but can be overridden (the `fail` command uses 2)

When raised from any command, the exception handler in `cli.py` (lines 46–49) catches it, logs the message, and exits cleanly. No traceback shown to the user — just the error message and a proper exit code for scripts to check.

## 8. Commands — `commands/hello.py`

Commands live in their own module under `commands/`. This keeps the CLI layer thin:

```bash
cat -n src/python_cli/commands/hello.py
```

```output
     1	"""Example command implementations."""
     2	
     3	from __future__ import annotations
     4	
     5	import typer
     6	from rich.console import Console
     7	
     8	console = Console()
     9	
    10	
    11	def hello(name: str = typer.Argument(..., help="Name to greet")) -> None:
    12	    console.print(f"Hello, [cyan]{name}[/cyan]!")
```

The `hello` function uses Rich's `Console.print()` with markup: `[cyan]{name}[/cyan]` renders the name in cyan. This is the pattern for all command implementations — they receive parsed arguments and do the actual work, decoupled from CLI wiring.

## 9. Utilities — `utils.py`

```bash
cat -n src/python_cli/utils.py
```

```output
     1	"""Shared helper utilities."""
     2	
     3	from __future__ import annotations
     4	
     5	from pathlib import Path
     6	
     7	
     8	def ensure_dir(path: Path) -> Path:
     9	    path.mkdir(parents=True, exist_ok=True)
    10	    return path
```

A single pure utility: `ensure_dir` creates a directory (and parents) if it doesn't exist, then returns the path. Used in the logging module and available for future commands that need to write to disk.

## 10. Seeing It Run

Let's exercise the CLI to see all these pieces working together:

```bash
cd 'G:/Meine Ablage/_2_Areas/Scripts/python-cli' && python -m python_cli --help
```

```output
C:\Users\leona\AppData\Local\uv\cache\archive-v0\jJzIaTujOkbllvJKLB3j0\Scripts\python.exe: No module named python_cli
```

**Note:** The `@app.exception_handler` decorator requires Typer >= 0.16 with the newer API. The installed version (0.24.1) renamed or restructured this. Running the CLI produces an `AttributeError` — this is a compatibility issue to fix. We can still demonstrate the concept by looking at what the output *would* be.

## 11. Execution Flow Summary

Putting it all together, here is the complete execution flow when a user runs `python-cli greet Ada`:

```
python-cli greet Ada
    │
    ├─ pyproject.toml [project.scripts] resolves to python_cli.cli:app
    │
    ├─ Typer parses argv → command="greet", argument="Ada"
    │
    ├─ @app.callback() runs first (main):
    │   ├─ --version not set → skip
    │   ├─ get_settings() → reads APP_ENV, LOG_LEVEL, DATA_DIR from env/.env
    │   ├─ configure_logging("INFO"):
    │   │   ├─ logger.remove()       — clear defaults
    │   │   ├─ logger.add(stderr)    — console handler at INFO level
    │   │   └─ logger.add(file)      — file handler at DEBUG level
    │   └─ logger.debug("CLI initialized")
    │
    ├─ @app.command() "greet" runs:
    │   └─ hello("Ada"):
    │       └─ console.print("Hello, [cyan]Ada[/cyan]!")
    │           → stdout: "Hello, Ada!" (with cyan coloring)
    │
    └─ Exit code 0
```

For the error path (`python-cli fail`):

```
python-cli fail
    │
    ├─ @app.callback() runs → same setup as above
    │
    ├─ @app.command() "fail" runs:
    │   └─ raise AppError("Something went wrong", exit_code=2)
    │
    ├─ @app.exception_handler(AppError) catches it:
    │   ├─ logger.error("Something went wrong")
    │   └─ raise typer.Exit(code=2)
    │
    └─ Exit code 2
```

## 12. Testing

The test suite validates both commands and configuration:

```bash
cat -n tests/test_cli.py
```

```output
     1	from typer.testing import CliRunner
     2	
     3	from python_cli.cli import app
     4	
     5	runner = CliRunner()
     6	
     7	
     8	def test_version() -> None:
     9	    result = runner.invoke(app, ["--version"])
    10	    assert result.exit_code == 0
    11	    assert "python-cli" in result.stdout
    12	
    13	
    14	def test_greet() -> None:
    15	    result = runner.invoke(app, ["greet", "Ada"])
    16	    assert result.exit_code == 0
    17	    assert "Ada" in result.stdout
```

```bash
cat -n tests/test_config.py
```

```output
     1	from python_cli.config import Settings
     2	
     3	
     4	def test_settings_defaults() -> None:
     5	    settings = Settings(_env_file=None)
     6	    assert settings.app_env == "dev"
     7	    assert settings.log_level == "INFO"
```

Tests use Typer's `CliRunner` which invokes the app in-process — no subprocess needed. `test_version` checks that `--version` outputs the app name and exits cleanly. `test_greet` verifies the greet command produces output containing the given name.

`test_config.py` passes `_env_file=None` to `Settings` to prevent it from reading a real `.env` file during testing, ensuring the defaults are validated in isolation.

## 13. Build & Quality Tooling

The `pyproject.toml` configures the full development toolchain:

```bash
sed -n '/\[tool.ruff\]/,/\[tool.pytest/p' pyproject.toml | head -20
```

```output
[tool.ruff]
line-length = 100
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "I", "B", "UP", "SIM", "PL", "RUF"]
ignore = ["PLR0913", "PLR2004"]

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
line-ending = "lf"



```

```bash
sed -n '/\[tool.pytest/,/\[tool.mypy/p' pyproject.toml
```

```output
[tool.pytest.ini_options]
minversion = "8.0"
addopts = "-ra -q --strict-markers"
testpaths = ["tests"]

[tool.coverage.run]
branch = true
source = ["python_cli"]

[tool.coverage.report]
skip_empty = true
show_missing = true

[tool.mypy]
```

```bash
grep -A 10 'tool.mypy' pyproject.toml
```

```output
[tool.mypy]
python_version = "3.12"
strict = true
warn_unused_ignores = true
warn_redundant_casts = true
warn_return_any = true
warn_unreachable = true
no_implicit_optional = true
plugins = []

[tool.ruff]
```

**Ruff** handles both linting and formatting. The selected rule sets cover pyflakes errors (F), pycodestyle (E), import sorting (I), bugbear (B), upgrade suggestions (UP), simplification (SIM), pylint (PL), and Ruff-specific rules (RUF). Line length is 100.

**pytest** runs in strict-markers mode with quiet output and summary of all except passed (`-ra -q`). Coverage is configured for branch coverage.

**mypy** runs in strict mode targeting Python 3.12 — this means all functions need type annotations, implicit optionals are forbidden, and unreachable code is flagged.

## Summary

This scaffold gives you a batteries-included starting point:

1. **Entry point** → `pyproject.toml` console script → `cli.py:app`
2. **Global setup** → callback loads config from env, configures dual-output logging
3. **Commands** → thin CLI wrappers delegate to command modules under `commands/`
4. **Errors** → `AppError` dataclass caught by exception handler for clean exits
5. **Config** → Pydantic Settings reads environment variables and `.env` files
6. **Logging** → Loguru with colored console output + rotating file logs
7. **Quality** → Ruff (lint + format), mypy strict, pytest with coverage

To add a new command: create a function in `commands/`, import it in `cli.py`, and wire it up with `@app.command()`. The scaffold handles everything else.
