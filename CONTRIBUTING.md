# Contributing

Thanks for considering a contribution.

## Development

```bash
uv sync --group dev
uv run pytest
uv run ruff check .
uv run ruff format .
```

## Guidelines

- Prefer small, focused changes.
- Add tests for behavior changes.
- Keep public CLI flags backward compatible when possible.
- Run linting and tests before submitting.

## TDD

We follow strict Red/Green/Refactor. New behavior must start with a failing test, then minimal code to pass, then refactor.

