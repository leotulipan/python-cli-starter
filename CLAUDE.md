# CLAUDE.md

## Shell Commands

Do NOT prefix commands with `cd` to the project root — cwd is already set. Just run commands directly with relative paths.

## Quick Reference

```bash
uv sync --group dev    # Install deps
uv run pytest          # Run tests
uv run ruff check .    # Lint
uv run ruff format .   # Format
uv run mypy src        # Type check
```

## TDD

Use strict red/green/refactor. Add a failing test first, make it pass, then refactor.

## Versioning

We follow [Semantic Versioning](https://semver.org): `MAJOR.MINOR.PATCH`.

- **MAJOR** — incompatible CLI changes (renamed/removed commands or flags, breaking config schema).
- **MINOR** — new backwards-compatible commands, flags, or features.
- **PATCH** — bug fixes and internal changes with no user-visible behavior change.

Bump the version in `src/<pkg>/version.py` and add a matching entry to `CHANGELOG.md` in the same commit.
