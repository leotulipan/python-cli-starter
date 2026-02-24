# Architecture

## Overview

This scaffold is structured for CLI-first workflows with clean separations:

- `cli.py`: User-facing commands and wiring.
- `config.py`: Settings loaded from environment and `.env`.
- `logging.py`: Centralized logging setup.
- `commands/`: Feature-specific command handlers.
- `utils.py`: Pure helpers.

## Design Principles

- Keep command functions thin; delegate to services or modules.
- Make side effects explicit and easy to test.
- Prefer pure functions for parsing/formatting.
- Treat CLI as a thin adapter around a core library.

## Error Handling

All expected failures should raise `AppError` with an exit code and user-friendly message.
Unexpected errors bubble up and are logged with stack traces when verbose is enabled.
