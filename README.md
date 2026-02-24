# Python CLI Scaffold

A modern, batteries-included scaffold for building robust Python CLI tools.

## Goals

- Clean `src/` layout with typed package
- Typer-based CLI with Rich output
- Structured logging (console + rotating file logs)
- Pydantic settings with `.env` support
- Fast lint/format via Ruff
- Static typing via mypy
- Tests via pytest + coverage
- Pre-commit hooks

## Quick Start

```bash
# Create venv and install
uv sync --group dev

# Run the CLI
uv run python-cli --help

# Run tests
uv run pytest

# Lint & format
uv run ruff check .
uv run ruff format .
```

## Project Layout

```
python-cli/
├── src/python_cli/         # Package code
│   ├── cli.py              # Typer app & commands
│   ├── config.py           # Settings (env + .env)
│   ├── logging.py          # Loguru config
│   ├── errors.py           # Custom exceptions
│   ├── utils.py            # Shared helpers
│   ├── commands/           # Subcommands
│   └── __main__.py         # python -m python_cli
├── tests/                  # Pytest
├── docs/                   # Docs
├── pyproject.toml           # Build + tooling config
└── research.md             # Analysis of prior CLIs
```

## Environment Configuration

Copy `.env.example` to `.env` and fill values. The config loader looks in:

1. Current working directory
2. User home directory

## Packaging

Build a wheel:

```bash
uv build --wheel
```

Install as a tool:

```bash
uv tool install --editable .
```

## Renaming From `python-cli`

If you use this repo as a starter, search/replace `python-cli` and rename the following paths so the package, binary, and build artifacts match your new name:

Files that reference `python-cli`:
- `install.sh`
- `pyproject.toml` (project name + console script entry point)
- `python-cli.spec` (PyInstaller spec)
- `README.md` (examples + layout)
- `docs/build.md`
- `scripts/build_exe.ps1`
- `scripts/build_exe.sh`
- `src/python_cli/cli.py` (version banner)
- `src/python_cli/logging.py` (default log dir + file name)
- `tests/test_cli.py` (asserted output)
- `.github/workflows/ci.yml` (working directory)

Directories and files to rename when you change the project name:
- Repo root folder `python-cli/`
- Package folder `src/python_cli/` and import references to `python_cli`
- PyInstaller spec file `python-cli.spec`
- Optional: default log folder `~/.python-cli/` in `src/python_cli/logging.py` (if you want a new log path)

## License

MIT

## TDD (Red/Green/Refactor)

We use strict red/green/refactor. Add a failing test first, make it pass, then refactor.


## Build (PyInstaller)

`ash
uv sync --group build
uv run pyinstaller --clean --onefile --name python-cli python-cli.spec
` 

See docs/build.md for details.

## CI

GitHub Actions runs lint, type-check, and tests on push/PR.


## TDD Loop

Use either Make or just to run the Red/Green/Refactor loop:

`ash
make tdd
# or
just tdd
` 

