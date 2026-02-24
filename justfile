# TDD loop commands

tdd:
  desc: Red/Green/Refactor
  cmds:
    - uv run pytest
    - uv run pytest
    - uv run ruff check .
    - uv run ruff format .
    - uv run mypy src

red:
  desc: Red - write failing test
  cmds:
    - uv run pytest

green:
  desc: Green - make tests pass
  cmds:
    - uv run pytest

refactor:
  desc: Refactor with checks
  cmds:
    - uv run ruff check .
    - uv run ruff format .
    - uv run mypy src

lint:
  cmds:
    - uv run ruff check .

format:
  cmds:
    - uv run ruff format .

typecheck:
  cmds:
    - uv run mypy src

test:
  cmds:
    - uv run pytest
