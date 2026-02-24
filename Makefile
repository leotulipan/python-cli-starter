.PHONY: tdd test red green refactor lint format typecheck

# Red/Green/Refactor loop
red:
	uv run pytest

green:
	uv run pytest

refactor:
	uv run ruff check .
	uv run ruff format .
	uv run mypy src

# Shortcuts

tdd: red green refactor

test:
	uv run pytest

lint:
	uv run ruff check .

format:
	uv run ruff format .

typecheck:
	uv run mypy src
