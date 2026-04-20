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

## Start a New Project From This Template

```bash
# 1. Clone without the template's git history
git clone --depth=1 https://github.com/<you>/python-cli.git my-tool
cd my-tool
rm -rf .git
git init

# 2. Install deps
uv sync --group dev

# 3. Rename the package and fill in pyproject metadata
#    (prompts for description, author, email, repo URL — defaults pulled from git config)
uv run python init.py my-tool --dry-run   # preview
uv run python init.py my-tool --commit    # apply + initial commit

# 4. Verify
uv run pytest
uv run my-tool --help
```

After this, push to your own remote:

```bash
git remote add origin git@github.com:<you>/my-tool.git
git push -u origin main
```

## Everyday Commands

```bash
uv sync --group dev        # install/update deps
uv run python-cli --help   # run the CLI
uv run pytest              # tests
uv run ruff check .        # lint
uv run ruff format .       # format
uv run mypy src            # type-check
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

